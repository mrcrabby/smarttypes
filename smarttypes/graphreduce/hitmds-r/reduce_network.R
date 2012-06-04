
library(ggplot2)

#emp.hours.data <- read.csv("/home/timmyt/Desktop/watermark/emp_level.csv", header=T)

#read network from disk
#make adjacency matrix
#make distance matrix
#reduce distance matrix
#write reduction to disk
#create reduction images


pdf(file='../io/blah.pdf')
print(
	ggplot(mpg, aes(displ, hwy))+geom_point()
)
dev.off()
print('Done!')






