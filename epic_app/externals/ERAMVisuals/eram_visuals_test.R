

data_raw <- read_csv("./epic_app/externals/ERAMVisuals/eram_summary_sample.csv")

# Check with full data
data <- data_raw
ERAMRadialPlot(data)

# Check with all zero values
data <- data_raw %>% mutate(value = 0)
ERAMRadialPlot(data)

# Check with few random entries
val <- sample(1:nrow(data),3)
data <- data_raw[val,]
ERAMRadialPlot(data)

# Check with small values
data <- data_raw[c(1,2,3,20,21),]
data$value <- c(0.2, 0.1, 0, 0.2, 1)
ERAMRadialPlot(data)

