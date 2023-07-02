import torch
import math
import itertools
class SNGCCA():
    def __init__(self, device):
        self.K_list = []
        self.a_list = []
        self.cK_list = []
        self.u_list = []
        self.device = device

        self.Momentum_V: list = [None] * 3
        self.Adam_V: list = [None] * 3
        self.Adam_M: list = [None] * 3

    def projL1(self, v, b):
        if b < 0:
            raise ValueError("Radius of L1 ball is negative: {}".format(b))
        if torch.norm(v, 1) < b:
            return v
        u, indices = torch.sort(torch.abs(v), descending=True)
        sv = torch.cumsum(u, dim=0)
        rho = torch.sum(u > (sv - b) / torch.arange(1, len(u) + 1).to(self.device), dim=0)
        theta = torch.max(torch.zeros_like(sv), (sv[rho - 1] - b) / rho)
        w = torch.sign(v) * torch.max(torch.abs(v) - theta, torch.zeros_like(v))
        return w

    def sqdist(self, X1, X2):
        n1 = X1.shape[1]
        n2 = X2.shape[1]
        D = torch.sum(X1 ** 2, dim=0).reshape(-1, 1).repeat(1, n2) + torch.sum(X2 ** 2, dim=0).reshape(1, -1).repeat(n1,1) - 2 * torch.mm(X1.T, X2)
        return D

    def gradf_gauss_SGD(self, K1, cK2, X, a, u):
        N = K1.shape[0]
        temp1 = torch.zeros((X.shape[1], X.shape[1])).to(self.device)
        au = a
        
        id1 = torch.sort(torch.rand(N))[1]
        id2 = torch.sort(torch.rand(N))[1]
        N = math.floor(N / 10)

        for i in range(N):
            for j in range(N):
                a = id1[i]
                b = id2[j]
                temp1 += K1[a, b] * cK2[a, b] * torch.ger(X[a, :] - X[b, :], X[a, :] - X[b, :]).to(self.device)
        final = -2 * au * u.t() @ temp1
        return final.t()

    def gene_SGD(self, K1, cK_list, X, a, u):
        res = torch.empty(u.shape[0], 1).to(self.device)
        for i in range((len(cK_list))):
            temp = self.gradf_gauss_SGD(K1, cK_list[i], X, a, u)
            res += temp
        return res

    def rbf_kernel(self, X, sigma=None):
        # 计算距离矩阵
        D = torch.sqrt(torch.abs(self.sqdist(X.t(), X.t())))

        if sigma is None:
            # 中位数启发式法估计 sigma
            sigma = torch.median(D)

        # 计算核矩阵
        K = torch.exp(- (D ** 2) / (2 * sigma ** 2))
        return K, sigma

    def centre_kernel(self, K):
        return K + torch.mean(K) - (torch.mean(K, dim=0).reshape((1, -1)) + torch.mean(K, dim=1).reshape((-1, 1)))

    def ff(self,K_list,cK_list):
        N = K_list[0].shape[0]
        res = 0
        for items in itertools.combinations(range(len(K_list)), 2):
            res += torch.trace(K_list[items[0]] @ cK_list[items[1]]) / ((N - 1) ** 2)
        return res

    def set_init(self,views,b):
        for i, view in enumerate(views):
            v = torch.rand(view.shape[1]).to(self.device)
            umr = torch.reshape(self.projL1(v, b[i]), (view.shape[1], 1))
            u_norm = umr / torch.norm(umr, p=2).to(self.device)

            ## Calculate Kernel
            Xu = view.to(self.device) @ u_norm
            sigma = None
            if sigma is None:
                K, a = self.rbf_kernel(Xu)
            else:
                K, a = self.rbf_kernel(Xu, sigma)
            cK = self.centre_kernel(K)
            
            ## Save Parameters
            self.K_list.append(K)
            self.a_list.append(a)
            self.cK_list.append(cK)
            self.u_list.append(u_norm)

    def fit(self, views, eps, maxit, b, loss="SGD", early_stopping=True, patience=10, logging=0):
        n_view = len(views)
        self.K_list = []
        self.a_list = []
        self.cK_list = []
        self.u_list = []
        self.set_init(views,b)

        diff = 99999
        ite = 0
        obj_list = []
        while (diff > eps) & (ite < maxit):
            ite += 1
            obj_origin = self.ff(self.K_list,self.cK_list)
            obj_new = obj_origin - 1
            #while obj_origin > obj_new:
            for i, view in enumerate(views):
                obj_old = self.ff(self.K_list,self.cK_list)
                cK_list_SGD = [self.cK_list[j] for j in range(n_view) if j != i]

                ## Calculate Delta and Gamma
                grad = self.gene_SGD(self.K_list[i], cK_list_SGD, view, self.a_list[i], self.u_list[i])
                gamma = torch.norm(grad, p=2)

                ## Start Line Search
                chk = 1
                while chk == 1:

                    u_norm = self._optim(i,self.u_list[i],grad,gamma,b[i],view_len=view.shape[1],loss=loss)
                    Xu_new = view.to(self.device) @ u_norm

                    sigma = None
                    if sigma is None:
                        K_new, a_new = self.rbf_kernel(Xu_new)
                    else:
                        K_new, a_new = self.rbf_kernel(Xu_new, sigma)
                    cK_new = self.centre_kernel(K_new)

                    ## update K
                    K_list_SGD = [self.K_list[j] for j in range(n_view) if j != i]
                    K_list_SGD.append(K_new)

                    ## update cK
                    cK_list_SGD = [self.cK_list[j] for j in range(n_view) if j != i]
                    cK_list_SGD.append(cK_new)
                    obj_new = self.ff(K_list_SGD,cK_list_SGD)

                    ## Update Params
                    if obj_new > obj_old + 1e-5 * abs(obj_old):
                        chk = 0
                        self.u_list[i] = u_norm
                        self.K_list[i] = K_new
                        self.cK_list[i] = cK_new
                        self.a_list[i] = a_new
                    else:
                        gamma = gamma / 2
                        if gamma < 1e-7:
                            chk = 0
                obj = obj_new
                # End Line Search

            diff = abs(obj_new - obj_old) / abs(obj_new + obj_old)
            obj_list.append(round(obj_new.item(),4))
            if logging == 1:
                print('iter=', ite, "diff=", diff, 'obj=', obj)

            if early_stopping is True:
                if self.EarlyStopping(obj_list,patience=patience):
                    return self.u_list
        if logging == 2:
            print("diff=", diff, 'obj=', obj)
        return self.u_list

    def _optim(self, i, u, grad, gamma, b, view_len, loss="SGD"):
        if loss == "SGD":   # SGD
            if gamma > torch.tensor(1e-2):
                gamma = torch.tensor(1e-2)
            v_new = torch.reshape(u + grad * gamma, (-1,))

        elif loss == "Momentum": # Momentum
            if gamma > torch.tensor(1e-2):
                gamma = torch.tensor(1e-2)

            if self.Momentum_V[i] is None:
                self.Momentum_V[i] = torch.zeros(view_len,1)
            v = self.Momentum_V[i]

            v = - 0.9 * v + grad * gamma
            self.Momentum_V[i] = v

            v_new = torch.reshape(u + v, (-1,))

        elif loss == "Adam":    # adam
            if self.Adam_M[i] is None:
                self.Adam_V[i] = torch.zeros(view_len, 1)
                self.Adam_M[i] = torch.zeros(view_len, 1)
            m = self.Adam_M[i]
            v = self.Adam_V[i]

            m = 0.9 * m + (1 - 0.9) * grad
            v = 0.999 * v + (1 - 0.999) * (grad ** 2)
            self.Adam_M[i] = m
            self.Adam_V[i] = v
            v_new = torch.reshape(u + gamma * m / (torch.sqrt(v) + 1e-8), (-1,))

        u_new = torch.reshape(self.projL1(v_new, b), (view_len, 1))
        u_norm = u_new / torch.norm(u_new, p=2)
        return u_norm

    def EarlyStopping(self,lst,patience=5):
        if len(lst) < patience:
            return False
        last_five = lst[-patience:]
        return len(set(last_five)) == 1
