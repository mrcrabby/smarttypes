
library(ggplot2)

graph_reduction <- read.csv("io/graph_reduction.csv", header=T)


ggplot(graph_reduction, aes(x=x_coordinate, y=y_coordinate, label=node_id)) + geom_point(shape=1)  






