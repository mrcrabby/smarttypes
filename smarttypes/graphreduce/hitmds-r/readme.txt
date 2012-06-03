Batch high throughput multidimensional scaline (HiT-MDS)
for R programming language

Quick start:

- extract files to directory (which You probably did already),
- start R
- cd to target directory (setwd),
- on prompt type> source("embed_genes.r")

A scatter plot of 1206 points display should appear
and form a sandglass shape of temporally up- and down-regulated genes.
Final correlation should be around r^2 ~ 0.853.

For smaller data sets restart multiple times for getting a best solution.

See program code for further information
end enjoy the program,
Marc Strickert 
(stricker@ipk-gatersleben.de)


FILES

stdscatter.r: helper to create a standardized orientation of the scatter plot by PCA

embed_genes.r: the caller to be source()d
hitmds.m: the R implementation of HiT-MDS

genes_endo_4824.dat: 14-dim data of regulated genes of developing barley endosperm tissue
see: http://www.biomedcentral.com/1471-2105/8/165

gp_license.txt: Licence text (GPLv2)


Further link: http://hitmds.webhop.net/

Leibniz-Institute of Plant Genetics and Crop Plant Research Gatersleben
http://www.ipk-gatersleben.de/

This work is kindly founded by the Ministry of Cultural Affairs of Sachsen Anhalt 
Grant: XP3624HP/0606T

Sun May 17 11:07:01     2009
// EOF
