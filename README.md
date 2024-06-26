### [Sparse Nonlinear Generalized Canonical Correlation Analysis with Applications in Multiview Genomic Datasets]()

Official Pytorch implementation of SNGCCA, from the following paper:

[Sparse Nonlinear Generalized Canonical Correlation Analysis with Applications in Multiview Genomic Datasets]().  \
Rong Wu, Ziqi Chen and Hai Shu. \
New York University \
[[`arXiv`]()]

---

<p align="center">
<img src="screenshots/Overview.jpg" width=100% height=40% 
class="center">
</p>

We propose **SNGCCA**.

 ## Installation
Clone this repository and install other required packages:
```
git clone git@github.com:Rows21/SNGCCA
```

 ## Datasets
  - [x] Synthetic Datasets [synth_data.py](/SNGCCA/synth_data.py)
  - [x] TCGA Breast Cancer Database [RealData](/SNGCCA/RealData/) from (https://tcga-data.nci.nih.gov/docs/publications)
 
 (Feel free to post suggestions in issues of recommending latest proposed CCA network for comparison. Currently, the network folder is to put the current SOTA models. We can further add the recommended network in it for training.)
 
 <!-- ✅ ⬜️  -->
 ## Results 
 ### Simulation Studies

<div class="main">
<div class="tag">
</div>
<div class="images" >
	<div class="mid">
		<img src="SNGCCA/Results/Figure2/Fig2a.png" />
	</div>
	<div class="mid">
		<img src="SNGCCA/Results/Figure2/Fig2b.png" />
	</div>
	<div class="mid">
		<img src="SNGCCA/Results/Figure2/Fig2c.png" />
	</div>
</div>
<div style="clear:both;"></div>
<div style="margin-bottom:30px;">
</div>
<p> <img src="SNGCCA/Results/Figure2/FigFR.png" width=100% height=40% class="center"> </p>

### Real-World Studies -- TCGA breast cancer database
<div class="main">
<div class="tag">
</div>
<div class="images" >
	<div class="mid">
		<img src="/screenshots/heatmap/Exp.JPG" />
	</div>
	<div class="mid">
		<img src="/screenshots/heatmap/Meth.JPG" />
	</div>
	<div class="mid">
		<img src="/screenshots/heatmap/miRNA.JPG" />
	</div>
</div>
<div style="clear:both;"></div>
<div style="margin-bottom:30px;">
</div>

<div class="main">
<div class="tag">
</div>
<div class="images" >
	<div class="mid">
		<img src="/screenshots/venndiagram/FigVenna.png" />
	</div>
	<div class="mid">
		<img src="/screenshots/venndiagram/FigVennb.png" />
	</div>
	<div class="mid">
		<img src="/screenshots/venndiagram/FigVennc.png" />
	</div>
</div>
<div style="clear:both;"></div>
<div style="margin-bottom:30px;">
</div>

## Acknowledgement
This repository is built using the [timm](https://github.com/rwightman/pytorch-image-models) library.

## License
This project is released under the MIT license. Please see the [LICENSE](LICENSE) file for more information.

## Citation
If you find this repository helpful, please consider citing:
```

```
