library(magrittr)
library(dplyr)
library(ggplot2)
library(e1071)
library(leaflet)

# setwd("C:/Users/cheekit/Desktop/shinyapp/Rshiny/app")
# Function utility:
# Here's the Decision Analysis Model; Probabilistic, Utility-Based Discrete Choice Model
utility <- function(studentBF,studentProfile,propertyMap,dump.covariates=FALSE){
  # studentBF must come in as a 1-row matrix!!!
  
  covarnames <- sapply(names(propertyMap),function(propnm){
    if(propnm == 'income'){
      return(propertyMap$income[[ifelse(studentProfile$dependent,
                                        'dependent',
                                        'independent')]][studentProfile[[propnm]]])
    }
    levelName <- studentProfile[[propnm]]
    if(is.null(levelName)) return(propertyMap[[propnm]]) 
    return(propertyMap[[propnm]][levelName])
  })
  if(is.null(dim(studentBF))) {
    xBF <- matrix(studentBF[covarnames],nrow=1,dimnames=list(NULL,covarnames))
  } else {
    xBF <- matrix(studentBF[,covarnames],nrow=1,dimnames=list(NULL,covarnames))
  }
  
  # Assign useful column names...
  colnames(xBF) <- paste(colnames(xBF),names(covarnames),sep=':')
  
  #show(xBF)
  
  # Compute the utility the student derives from the school.
  beta <- setNames(studentProfile$beta,colnames(xBF))
  u    <- xBF %*% beta
  
  if (dump.covariates){
    wxBF <- xBF * matrix(beta,nrow=nrow(xBF),ncol=ncol(xBF),byrow = TRUE)
    colnames(wxBF) <- colnames(xBF)
    return(wxBF)
  } else {
    return(u[1])
  }
}
#===================================================================
# Function getParameters:
getParameters <- function(studentProfile,propertyMap){
  beta <- matrix(rep(1,length(propertyMap)),ncol=1)
  rownames(beta) <- names(propertyMap)
  
  weightLvls    <- setNames(as.list(studentProfile$weight),c('IncomeWeight','LocaleWeight','RegionWeight','SATWeight'))
  
  # assumes stronger influence of gender for women than men...
  beta['gender'   ,1] <- ifelse(studentProfile$gender == 'female',0.5,-0.1) 
  #increase weight if weight is medium or high, else remain the same
  if(weightLvls$IncomeWeight=="H")
    beta['income',1] <- 4 * beta['income',1]
  else if(weightLvls$IncomeWeight=="M")
    beta['income',1] <- 2 * beta['income',1]
  if(weightLvls$LocaleWeight=="H")
    beta['locale',1] <- 4 * beta['locale',1]
  else if(weightLvls$LocaleWeight=="M")
    beta['locale',1] <- 2 * beta['locale',1]
  if(weightLvls$RegionWeight=="H")
    beta['region',1] <- 4 * beta['region',1]
  else if(weightLvls$RegionWeight=="M")
    beta['region',1] <- 2 * beta['region',1]
  if(weightLvls$SATWeight=="H")
    beta['sat',1] <- 4 * beta['sat',1]
  else if(weightLvls$SATWeight=="M")
    beta['sat',1] <- 2 * beta['sat',1]
  
  # Also, make the beta's of traits sum to 1 at each level so that final utility
  # is roughly same magnitude as a typical Bayes factor for school properties.
  # This facilitates interpretation of utility in similar fashion as a raw Bayes factor.
  beta[,1] <- beta[,1]/sum(abs(beta[,1]))
  
  return(beta)
}
#================================================================
# recommendColleges to assess the suitability of colleges for a specific student's profile and recommend it with  a ranking:
recommendColleges <- function(studentBF,stdtProf,propertyMap,ntop=20,signifLevel=0.15,verbose=FALSE,exact=FALSE){
  utilities <- studentBF %>% 
    dplyr::select(-c(1:3),-c(41:43)) %>%
    apply(1,utility,studentProfile=stdtProf,propertyMap=propertyMap) %>%
    setNames(studentBF$College)
  
  tmp <- studentBF %>% 
    dplyr::select(-c(1:3),-c(41:43)) %>%
    slice(1) %>% as.matrix %>%
    utility(studentProfile=stdtProf,propertyMap=propertyMap,dump.covariates=TRUE)
  
  wxBF <- studentBF %>% 
    dplyr::select(-c(1:3),-c(41:43)) %>%
    apply(1,utility,studentProfile=stdtProf,propertyMap=propertyMap,dump.covariates=TRUE) %>%
    t %>% as.data.frame %>% tbl_df %>%
    setNames(gsub('^[^:]+:','',colnames(tmp))) %>%
    mutate(unitID  = studentBF$unitID,
           College = studentBF$College,
           Utility = utilities) %>% 
    arrange(desc(Utility)) %>%
    dplyr::select(unitID,College,Utility,everything())
  
  labels <- sprintf("%d. %s",order(order(utilities,decreasing=TRUE)),names(utilities))
  
  stdtUtility <- data_frame(unitID  = studentBF$unitID, 
                            College = names(utilities),
                            Utility = utilities) %>%
    mutate(labels = factor(labels,levels=labels[order(Utility,decreasing=TRUE)]),
           expChoice = 10^Utility,
           ChoicePct = 100*expChoice/sum(expChoice)) %>%
    dplyr::select(-expChoice) %>%
    inner_join(wxBF %>% dplyr::select(-College,-Utility),by='unitID') %>% 
    arrange(desc(Utility)) #%T>% print
  
  topN <- stdtUtility %>% dplyr::select(-College) %>% top_n(ntop,Utility) 
  
  predictInput <- stdtUtility %>% top_n(ntop,Utility)  %>% dplyr::select(-College,-unitID,-Utility,-labels,-ChoicePct)

  if(verbose) {
    topN %>% print
    profText <- stdtProf[!grepl('beta',names(stdtProf))]
    pltTitle <- paste(strwrap(paste(paste(names(profText),profText,sep=':'),collapse=', '),width = 80),collapse='\n')
    pltTitle <- paste0("Top ",ntop," Colleges for Profile:\n",pltTitle)
    
    gplt0 <- topN %>% 
      mutate(labels = factor(labels,levels=rev(levels(labels))),
             labelY = pmin(0,min(Utility))) %>%
      ggplot(aes(x=labels,y=Utility,fill=labels))
    gplt <-  gplt0 +
      geom_bar(stat='identity',position='dodge') + coord_flip() + 
      geom_text(aes(x=labels,y=labelY,label=labels),size=6,hjust=0,vjust=0.5) +
      theme(text=element_text(face='bold',size=8),
            axis.text.y=element_blank(),
            title=element_text(size=12,face='bold'),
            legend.position = "none") +
      ggtitle(pltTitle) +
      labs(x=sprintf("Top %d Colleges",ntop)) 
    gplt %>% print
  }
  
  # Back-calculate the beta coefficients and see if can determine which
  # covariate contributed most strongly to the utility rankings.
  stdtBF <- stdtUtility %>% 
    inner_join(studentBF %>% dplyr::select(-College),by='unitID')
  axbf <- stdtBF %>% dplyr::select(one_of(gsub('^[^:]+:','',colnames(tmp)))) %>% as.matrix
  betacoeff <- solve(t(axbf) %*% axbf,t(axbf) %*% matrix(stdtUtility$Utility,ncol=1))
  
  if(verbose) show(betacoeff[betacoeff>1.0E-9,])
  
  stdtBF %<>%
    dplyr::select(c(4,3,5),one_of(names(betacoeff[abs(betacoeff)>1.0E-9,]))) 
  
  if(verbose) stdtBF %>% print(n=ntop,width=Inf)
  
  utlBFcor <- stdtBF %$% 
    lapply(.[-(1:3)],function(y) cor.test(Utility[1:ntop],y[1:ntop],method='spearman',exact=exact)) #%T>% print
  
  # This shows which covariates dictate the rankings by utility. If significant
  # negative correlation, then that covariate is important in the latter half of
  # the ranking (note that reverse ordering due to negative coefficients is
  # already accounted for).
  pvals <- sapply(utlBFcor,'[[','p.value')
  pvals <- pvals[!is.na(pvals)]
  
  signifCor <- utlBFcor[pvals <= pmax(signifLevel,min(pvals,na.rm=TRUE))] %$% {.[order(sapply(.,'[[','p.value'))]}
  
  if(verbose) signifCor %>% show
  
  results <- list(student=stdtProf,topN=topN,predictInput=predictInput,utilities=stdtUtility,BF=stdtBF,cor=utlBFcor,signifCor=signifCor,beta=betacoeff)
  invisible(results)
}
#================================================================
recommendTopN <- function(caseResult,keyprop='region',plot.it=TRUE){
  propnm <- keyprop
  dataLength <- nrow(caseResult$topN)
  stdtProf <- caseResult$student
  profText <- c(stdtProf[propnm],stdtProf[!grepl(paste0('beta|',propnm),names(stdtProf))])
  # pltTitle <- paste(strwrap(paste(paste(names(profText),profText,sep=':'),collapse=', '),width = 80),collapse='\n')
  pltTitle <- paste(sprintf("Top %d Colleges for Profile:\n",dataLength))
  
  
  #offset all so that sum = 0
  offset<-sum(caseResult$topN[,2])
  caseResult$topN[,2]<-caseResult$topN[,2]-offset/dataLength
  #result then + avg probability to get actual probability
  caseResult$topN[,2]<-100/dataLength+caseResult$topN[,2]
  
  gplt0 <- caseResult$topN %>% 
    mutate(labels = factor(labels,levels=rev(levels(labels))),
           labelY = pmin(0,min(Utility))) %>%
    ggplot(aes(x=labels,y=Utility,fill=labels))
  gplt <-  gplt0 +
    geom_bar(stat='identity',position='dodge') + coord_flip() + 
    geom_text(aes(x=labels,y=labelY,label=labels),size=6,hjust=0,vjust=0.5) +
    theme(text=element_text(face='bold',size=8),
          axis.text.y=element_blank(),
          title=element_text(size=12,face='bold'),
          legend.position = "none") +
    ggtitle(pltTitle) +
    labs(x=sprintf("Top %d Colleges",dataLength)) +
    labs(y="Probability")

  if(plot.it) print(gplt)
  return(gplt) 
}
#================================================================
recommendTopNEarning <- function(caseResult,prediction,keyprop='region',plot.it=TRUE){
  dataLength <- nrow(caseResult$topN)
  gplt0 <- caseResult$topN %>% 
    mutate(labels = factor(labels,levels=rev(levels(labels))),
           labelY = pmin(0,min(prediction))) %>%
    ggplot(aes(x=labels,y=prediction,fill=labels))
  gplt <-  gplt0 +
    geom_bar(stat='identity',position='dodge') + coord_flip() + 
    geom_text(aes(x=labels,y=labelY,label=labels),size=6,hjust=0,vjust=0.5) +
    theme(text=element_text(face='bold',size=8),
          axis.text.y=element_blank(),
          title=element_text(size=12,face='bold'),
          legend.position = "none") +
    ggtitle("Predicted Earning for Colleges") +
    labs(x=sprintf("Top %d Colleges",dataLength)) +
    labs(y="Predicted Earning")

  if(plot.it) print(gplt)
  return(gplt) 
}
#================================================================
overviewMap <- function(caseResult,student){
  mortarBoardIcon <- makeIcon(
  iconUrl = "https://image.flaticon.com/icons/svg/169/169856.svg",
  iconWidth = 30, iconHeight = 30)

  schools <- caseResult$topN %>%
    inner_join(student %>% 
                 dplyr::select(c(2:3),c(42:43)), by='unitID') %>%
    mutate(info = paste0(sprintf('<br>Rank: %d,College Name:%s',seq_along(Utility),College)))
  map <- leaflet(schools) %>% 
    setView(-113, 42, zoom = 4) %>%
    addTiles() %>%
    addMarkers(~Longitude, ~Latitude, popup=~info,
               options = popupOptions(closeButton = TRUE),
               clusterOptions = markerClusterOptions(), 
               icon = mortarBoardIcon)
  return(map) 
  invisible(map)
}
#================================================================
propertyMap <- list(
  ethnicity  = c(white    = 'White',
                 black    = 'Black',
                 hispanic = 'Hispanic',
                 asian    = 'Asian',
                 american_alaska = 'AmericanIndianOrAlaskaNative',
                 hawaiian_pacific = 'NativeHawaiianOrPacificIslander',
                 two_more_races = 'TwoOrMoreRaces',
                 non_resident = 'NonResidentAliens',
                 race_unknown = 'RaceUnknown'),
  income     = list(dependent   = c(le30K       = "Dependent_30k",
                                    gt30Kle110K = "Dependent_30_110K",
                                    gt110K      = "Dependent_110k"),
                    independent = c(le30K       = "Independent_30k",
                                    gt30Kle110K = "Independent_30_110k",
                                    gt110K      = "Independent_110k")),
  sat        = c(le800        = 'lwr800',  
                 gt800le1000  = 'btwn800_1000', 
                 gt1000le1200 = 'btwn1000_1200', 
                 gt1200le1400 = 'btwn1200_1400', 
                 gt1400='gtr1400'),
  region     = c(FarWest        = 'FarWest',
                 GreatLakes     = 'GreatLakes',
                 MidEast        = 'MidEast',
                 NewEngland     = 'NewEngland',
                 Plains         = 'Plains',
                 RockyMountains = 'RockyMountains',
                 Southeast      = 'SouthEast',
                 Southwest      = 'SouthWest'),
  locale     = c(Rural          = 'Rural',
                 TownRemote     = 'TownRemote',
                 TownDistant    = 'TownDistant',
                 SuburbSmallMid = 'SmallSuburb',
                 SuburbLarge    = 'LargeSuburb',
                 CitySmall      = 'SmallCity',
                 CityMidsize    = 'MidCity',
                 CityLarge      = 'LargeCity'),
  gender     = c(female = 'Female',
                 male   = 'Female')
)
studentBF <- read.csv("all6.csv", 
                      header = TRUE)

profile <- function(p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11){
  if (p3 == 'TRUE') {
    Profile = list(
      dependent = TRUE,           
      ethnicity = p2,     
      gender    = p1,         
      income    = p4,  
      sat       = p6,     
      region    = p10,      
      locale    = p8,
      weight    = list(          
        incomeWeight  = p5,
        localeWeight = p9,
        regionWeight = p11,
        SATweight = p7) 
    )
  }else {
    Profile = list(
      dependent = FALSE,           
      ethnicity = p2,     
      gender    = p1,         
      income    = p4,  
      sat       = p6,     
      region    = p10,      
      locale    = p8,
      weight    = list(          
        incomeWeight  = p5,
        localeWeight = p9,
        regionWeight = p11,
        SATweight = p7) 
    )
  }
  return(Profile)
}

chasingdreamschool <- function(stu,ntop){
  stu$beta <- getParameters(stu,propertyMap)
  caseResult          <- recommendColleges(studentBF,stu,propertyMap,verbose=FALSE,ntop=ntop)
  recommendTopN(caseResult,plot.it = TRUE)
}

chasingdreamschoolEarning <- function(stu,ntop){
  #ntop <- 10
  stu$beta <- getParameters(stu,propertyMap)
  caseResult          <- recommendColleges(studentBF,stu,propertyMap,verbose=FALSE,ntop=ntop)
  
  model = readRDS("final_model.rds")
  top10 = as.data.frame(caseResult["predictInput"])
  colnames(top10) <- c('PC1','PC2','PC3','PC4','PC5','PC6')
  prediction = data.frame(predict(model,top10))
  
  recommendTopNEarning(caseResult,prediction,plot.it = TRUE)
}
chasingdreamschoolMap <- function(stu,ntop){
  #ntop <- 10
  stu$beta <- getParameters(stu,propertyMap)
  caseResult          <- recommendColleges(studentBF,stu,propertyMap,verbose=FALSE,ntop=ntop)
  
  overviewMap(caseResult,studentBF)
}
