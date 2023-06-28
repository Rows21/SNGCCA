# 引入必要的库
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle
from sklearn import svm, datasets
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc, confusion_matrix, classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize, StandardScaler
from sklearn.multiclass import OneVsRestClassifier
from scipy import interp

# 加载数据
Exp_label = pd.read_csv('RealData/Exp664_genes.txt', sep='\t',header = None)
Exp_list = Exp_label.iloc[:, 0].values.tolist()
Exp = pd.DataFrame(np.loadtxt("RealData/Exp664.txt").T,columns = Exp_label)

# labels
y = pd.read_csv('RealData/PAM50label664.txt',header = None).values
#X = Exp
ExpRes = pd.read_csv("./Results/Exp_score.csv").values
listname = ExpRes[:,0]
FilterRes = []
for i in range(len(listname)):
    list_index: int = Exp_list.index(listname[i])
    FilterRes.append(list_index)

ExpFilter = Exp.iloc[:,FilterRes]

X = ExpFilter
# 将标签二值化
#y = label_binarize(y, classes=[1, 2, 3,4])  # 三个类别

# 设置种类
n_classes = y.shape[1]

# 训练模型并预测
random_state = np.random.RandomState(0)
#n_samples, n_features = X.shape

# shuffle and split training and test sets
X_train, X_test, y_train, y_test = train_test_split(Exp, y, test_size=0.3, random_state=0)

# Learn to predict each class against the other
scaler = StandardScaler()
Exp = scaler.fit_transform(Exp)

clf_rf = RandomForestClassifier(n_estimators=50, criterion='entropy', random_state=0)
clf_rf.fit(X_train, y_train)

y_pred = clf_rf.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
cr = classification_report(y_test, y_pred)
acc = accuracy_score(y_test, y_pred)
print(cm,cr,acc)

# shuffle and split training and test sets
X_train, X_test, y_train, y_test = train_test_split(ExpFilter, y, test_size=0.3, random_state=0)

# Learn to predict each class against the other
scaler = StandardScaler()
Exp = scaler.fit_transform(Exp)

clf_rf = RandomForestClassifier(n_estimators=50, criterion='entropy', random_state=0)
clf_rf.fit(X_train, y_train)

y_pred = clf_rf.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
cr = classification_report(y_test, y_pred)
acc = accuracy_score(y_test, y_pred)
print(cm,cr,acc)

clf_svm = OneVsRestClassifier(svm.SVC(kernel='rbf', probability=True, random_state=random_state))
y_score = clf_svm.fit(X_train, y_train).predict_proba(X_test)  # 获得预测概率

# 计算每一类的ROC
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# Compute micro-average ROC curve and ROC area（方法二）
fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_score.ravel())
roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

# Compute macro-average ROC curve and ROC area（方法一）
# First aggregate all false positive rates
all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))

# Then interpolate all ROC curves at this points
mean_tpr = np.zeros_like(all_fpr)
for i in range(n_classes):
    mean_tpr += interp(all_fpr, fpr[i], tpr[i])

# Finally average it and compute AUC
mean_tpr /= n_classes
fpr["macro"] = all_fpr
tpr["macro"] = mean_tpr
roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

# Plot all ROC curves
lw = 2
plt.figure()
plt.plot(fpr["micro"], tpr["micro"],
         label='micro-average ROC curve (area = {0:0.2f})'
               ''.format(roc_auc["micro"]),
         color='deeppink', linestyle=':', linewidth=4)

plt.plot(fpr["macro"], tpr["macro"],
         label='macro-average ROC curve (area = {0:0.2f})'
               ''.format(roc_auc["macro"]),
         color='navy', linestyle=':', linewidth=4)

colors = cycle(['aqua', 'darkorange', 'cornflowerblue','pink'])
for i, color in zip(range(n_classes), colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=lw,
             label='ROC curve of class {0} (area = {1:0.2f})'
                   ''.format(i, roc_auc[i]))

plt.plot([0, 1], [0, 1], 'k--', lw=lw)
plt.xlim([-0.02, 1.0])
plt.ylim([0.0, 1.02])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Some extension of Receiver operating characteristic to multi-class')
plt.legend(loc="lower right")
#plt.show()