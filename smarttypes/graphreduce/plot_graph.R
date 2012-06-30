

library(diffusionMap)
library(ggplot2)


similarity_matrix = read.csv("io/similarity_matrix.csv", header=FALSE, sep=",")
#reduction = diffuse(similarity_matrix, neigen=2)

#faster but need to id dimensions ahead of time
#A <- matrix(scan("matrix.dat", n = 200*2000), 200, 2000, byrow = TRUE)



#graph_reduction <- read.csv("io/graph_reduction.csv", header=T)
#ggplot(graph_reduction, aes(x=x_coordinate, y=y_coordinate, label=node_id)) + geom_point(shape=1)  






