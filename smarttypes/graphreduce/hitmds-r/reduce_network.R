
library(ggplot2)

#emp.hours.data <- read.csv("/home/timmyt/Desktop/watermark/emp_level.csv", header=T)

pdf(file='../io/blah.pdf')
print(
	ggplot(mpg, aes(displ, hwy))+geom_point()
)
dev.off()
print('Done!')






