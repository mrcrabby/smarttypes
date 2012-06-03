source("hitmds.r")
source("stdscatter.r")

# data vectors are arranged as rows
dat <- as.matrix(read.table('genes_endo_4824.dat'))

dat <- dat[seq(1,nrow(dat),by=4),] # only each fourth vector for illustration

# Euclidean distance matrix (leads to embedding results, similar to PCA)
#MD <- as.matrix(dist(dat,diag=T,upper=T))
# 1-correlation (Pearson) similarity matrix
MD <- (1 - cor(t(dat)))^8

### ! zero entries in MD denote absence of forces !
### useful for dealing with partial information

d_goal <- 2   # target dimension
l_rate <- .05  # learning rate
n_cyc  <- 25  # number of cycles

d_inp  <- ncol(dat)

# initialize y by random projection
y <- dat %*% (2 * (matrix(runif(d_inp * d_goal), d_inp, d_goal) - .5))

# do the work
y <- hitmds(MD, y, d_goal, l_rate, n_cyc, plt=TRUE)

# standardize HiT-MDS output
y <- stdscatter(y)

plot(y[,1],y[,2],'p',cex=.1)
text(y[,1]+.05,y[,2],paste(1:nrow(y)))
