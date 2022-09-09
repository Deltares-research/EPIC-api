#! /usr/bin/Rscript

# Install requred R packages (if not already installed)
if (!require(scales)) {
    install.packages(scales)
}
if (!require(ggplot2)) {
    install.packages(ggplot2)
}
if (!require(dplyr)) {
    install.packages(dplyr)
}
if (!require(readr)) {
    install.packages(readr)
}

# R function to create the Radial plot
source("./ERAMRadialPlot.R")

# Get arguments, we only care for the first one
args <- commandArgs(trailingOnly = TRUE)
# Read-in tabular data from a csv file to create the visual
data <- readr::read_csv(args[[1]])

# Generate radial plot based on the data
p <- ERAMRadialPlot(data)

# Save plot to png
ggplot2::ggsave(filename = "radialplot.png", plot = p, width = 8, height = 8)

# Save plot to pdf
ggplot2::ggsave(filename = "radialplot.pdf", plot = p, width = 8, height = 8)
