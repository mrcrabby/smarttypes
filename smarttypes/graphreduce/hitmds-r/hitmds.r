hitmds <- function(D, Y, n_dim=2, rate=1, n_cycles=50, plt=TRUE) {
#HITMDS High-Throughput Dimensional Scaling (HiT-MDS)
#
# Y = hitmds(D, Y, n_dim, rate, n_cycles, plt)
#
# Embed dissimilarity matrix D into n_dim -dimensional Euclidean vector space.
#
# Arguments:
# D - source dissimilarity matrix
# Y  - initial target point configuration, leave empty {} for auto-init
# rate - try values {0.1 1 10 100} for optimum embedding, start using rate=1
# n_cycles - value between 10 and 5000, depending on number of data vectors;
#            the more data vectors, the less cycles are necessary.
# plt - if TRUE: plot intermediate results in 2D
#
# Return:
# Y - non-standardized embedded points (apply stdscatter for standardization)
#
# Watch value output after each iteration. The higher, the better.
# 0 means perfect mismatch of embedded data relations with D
# 1 means perfect reconstruction, i.e. most trustful embedding result.
#
# Severals runs are advisable for selecting optimum embedding results.
#
#
#
# Author:      Marc Strickert
# Institution: Leibniz-Institute of Crop Plant Research, IPK-Gatersleben
# Date:  Wed Feb 25 13:15:25     2009
# Licence:     GPLv2; not for use in critical applications

  eps <- 1e-15

  if(!is.matrix(D))
    stop('D no matrix!')

  n_data <- nrow(D)

  zers <- which(D == 0)

  n_datainvs <- 1. / (n_data * n_data - length(zers))

  if(n_dim == 1 && length(Y) > 0 && !is.matrix(Y))
    Y <- as.matrix(Y)

  if(length(Y) > 0 && (nrow(Y) != n_data || ncol(Y) != n_dim))
    stop('Y matrix has wrong size!')

  # random point initialization if necessary, not very good,
  # better: random projection if available
  if(length(Y) == 0)
    Y <- 2 * (matrix(runif(n_data*n_dim), n_data, n_dim) - .5)

  mn_D <-  sum(D) * n_datainvs
  D <- D - mn_D
  D[zers] <- 0
  mo_D <-  sum(D * D)

  pnt_del <- Y
  T <- D

  for(i in seq(n_cycles,1,-1)) {

    T <- as.matrix(dist(Y, diag=T, upper=T))

    T[zers] <- 0
    
    mn_T <- sum(T) * n_datainvs
    T <- T - mn_T
    T[zers] <- 0 # unknowns: zero force
    
    
    mi_T <- sum(T * D)
    mo_T <- sum(T * T)

    f <- 2 / (abs(mi_T) + abs(mo_T))
    mi_T <- mi_T * f
    mo_T <- mo_T * f

      
    # correlation quality output log
    print(sqrt(mi_T * mi_T / (mo_D * mo_T * f)))

    tmpT <- T * mi_T - D * mo_T
    T <- T + (0.1 + mn_T)
    tmpT <- tmpT / T
   
    # calc point i update strength 
    for(j in 1:n_dim) {
      tmp <- Y[,rep(j,n_data)]
      tmp <- t(tmp) - tmp
      tmp = tmp * tmpT
      pnt_del[,j] = apply(tmp,1,sum)
    }

    Y <- Y + rate * i * .25 * (1+ i %% 2) / n_cycles * pnt_del / sqrt(abs(pnt_del)+.001)

    if(plt) {
      plot(Y[,1],Y[,2],'p',cex=1)
    }

  } # while
 
  Y
} # function
