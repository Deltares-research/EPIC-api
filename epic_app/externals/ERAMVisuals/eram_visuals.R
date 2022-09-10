#! /usr/bin/Rscript

ERAMRadialPlot <- function(data.to.plot, empty_bar = 2,
                           ymin = -60, ymax = 140, label_size = 2) {
  require(scales)
  require(ggplot2)
  require(dplyr)

  cols <- c("E" = "#1b9e77", "P" = "#d95f02", "I" = "#7570b3", "C" = "#e7298a", "R" = "#66a61e")

  # Scale values between 20 and 80
  data <- tibble::tribble(
    ~group, ~sub, ~individual, ~value,
    "E", "National Sectoral Frameworks", "Water Resource Management", 0L,
    "E", "National Sectoral Frameworks", "Disaster Risk Management", 0L,
    "E", "National Sectoral Frameworks", "Drought Risk Management", 0L,
    "E", "National Sectoral Frameworks", "Flood Risk Management", 0L,
    "E", "Whole-of-Society Approach", "Local Government", 0L,
    "E", "Whole-of-Society Approach", "Public & Stakeholder Engagement", 0L,
    "E", "Whole-of-Society Approach", "Social Inclusion", 0L,
    "E", "Whole-of-Society Approach", "Education & Risk Communication", 0L,
    "E", "Whole-of-Society Approach", "Scientific Collaboration", 0L,
    "E", "Whole-of-Society Approach", "Open Data", 0L,
    "E", "Hydrological and Meteorological Services", "National Framework NMS & NHS", 0L,
    "E", "Hydrological and Meteorological Services", "Co-production of services", 0L,
    "P", "Flood and Drought Risk Mitigation and Contingency Planning", "Integrated River Basin Planning", 0L,
    "P", "Flood and Drought Risk Mitigation and Contingency Planning", "Coastal Zone Management Planning", 0L,
    "P", "Flood and Drought Risk Mitigation and Contingency Planning", "Urban Water Supply Planning", 0L,
    "P", "Flood and Drought Risk Mitigation and Contingency Planning", "Irrigation Water Supply Planning", 0L,
    "P", "Flood and Drought Risk Mitigation and Contingency Planning", "Local Flood Risk Mitigation Planning", 0L,
    "I", "Healthy Watersheds", "Climate Smart Agriculture", 0L,
    "I", "Healthy Watersheds", "Forest Management", 0L,
    "I", "Healthy Watersheds", "Wetlands Management", 0L,
    "I", "Healthy Watersheds", "Local Watershed Mgt Organizations", 0L,
    "I", "Healthy Watersheds", "Watershed Management", 0L,
    "I", "Water Resources Infrastructure", "Water Resources Investment Policy", 0L,
    "I", "Water Resources Infrastructure", "Dam Safety", 0L,
    "I", "Water Resources Infrastructure", "Flood Infrastructure Safety", 0L,
    "C", "Water Allocation and Groundwater Management", "Flexible Water Allocation", 0L,
    "C", "Water Allocation and Groundwater Management", "Conjunctive Groundwater Mgt", 0L,
    "C", "Floodplain Management", "Floodplain Mapping", 0L,
    "C", "Floodplain Management", "Floodplain Regulation", 0L,
    "C", "Floodplain Management", "Local Flood Mitigation Planning", 0L,
    "R", "Drought Monitoring, Response and Recovery", "Drought Monitoring Program", 0L,
    "R", "Drought Monitoring, Response and Recovery", "WRM Drought Response", 0L,
    "R", "Drought Monitoring, Response and Recovery", "Agriculture Drought Response", 0L,
    "R", "Drought Monitoring, Response and Recovery", "Social Protection Drought Response", 0L,
    "R", "Flood Monitoring, Response and Recovery", "Flood Forecasting and Warning", 0L,
    "R", "Flood Monitoring, Response and Recovery", "Flood Emergency Prep, Resp and Relief", 0L,
    "R", "Flood Monitoring, Response and Recovery", "Flood Disaster Recovery", 0L,
    "R", "Disaster Risk Financing", "Disaster Risk Financing Instruments", 0L
  )

  prog_levels <- data$individual

  data <- data %>%
    mutate(group = factor(group, levels = c("P", "I", "C", "R", "E"))) %>%
    mutate(individual = factor(individual, levels = prog_levels)) %>%
    arrange(group)

  data2 <- data.to.plot %>%
    mutate(group = factor(group, levels = c("P", "I", "C", "R", "E"))) %>%
    mutate(individual = factor(individual, levels = prog_levels)) %>%
    arrange(group) %>%
    mutate(value = scales::rescale(value, to = c(20, 80)))

  mindex <- which(data$individual %in% data2$individual)
  data$value[mindex] <- data2$value

  # Set a number of 'empty bar' to add at the end of each group
  to_add <- data.frame(matrix(NA, empty_bar * nlevels(data$group), ncol(data)))
  colnames(to_add) <- colnames(data)
  to_add$group <- rep(levels(data$group), each = empty_bar)
  data <- rbind(data, to_add)
  data <- data %>% arrange(group)
  data$id <- seq(1, nrow(data))

  # Data frame to store the labels
  label_data <- data
  number_of_bar <- nrow(label_data)
  angle <- 90 - 360 * (label_data$id - 0.5) / number_of_bar
  label_data$hjust <- ifelse(angle < -90, 1, 0)
  label_data$angle <- ifelse(angle < -90, angle + 180, angle)

  # Data frame to store base lines
  base_data <- data %>%
    group_by(group) %>%
    summarize(start = min(id), end = max(id) - empty_bar) %>%
    rowwise() %>%
    mutate(title = mean(c(start, end)))

  # Data frame to store grids
  grid_data <- base_data
  grid_data$end <- grid_data$end[c(nrow(grid_data), 1:nrow(grid_data) - 1)] + 1
  grid_data$start <- grid_data$start - 1
  grid_data <- grid_data[-1, ]

  label_data2 <- filter(label_data, value > 0)
  label_dataNA <- filter(label_data, value == 0)



  # Make the plot
  p <- ggplot(data, aes(x = as.factor(id), y = value, fill = group)) +

    # Set main bars
    geom_bar(aes(x = as.factor(id), y = value), fill = "gray", stat = "identity", alpha = 0.8) +

    # Set segments
    geom_segment(
      data = grid_data, aes(x = end, y = 80, xend = start, yend = 80),
      colour = "grey50", alpha = 1, size = 0.5, inherit.aes = F
    ) +
    geom_segment(
      data = grid_data, aes(x = end, y = 60, xend = start, yend = 60),
      colour = "grey50", alpha = 1, size = 0.5, inherit.aes = F
    ) +
    geom_segment(
      data = grid_data, aes(x = end, y = 40, xend = start, yend = 40),
      colour = "grey50", alpha = 1, size = 0.5, inherit.aes = F
    ) +
    geom_segment(
      data = grid_data, aes(x = end, y = 20, xend = start, yend = 20),
      colour = "grey50", alpha = 1, size = 0.5, inherit.aes = F
    ) +

    # Set yaxis scales
    annotate("text",
      x = rep(max(data$id), 4), y = c(20, 40, 60, 80),
      label = c("1", "2", "3", "4"),
      color = "grey50", size = 5,
      angle = 0, fontface = "bold", hjust = 1
    ) +
    ylim(ymin, ymax) +
    theme_minimal() +
    theme(
      legend.position = "none",
      axis.text = element_blank(),
      axis.title = element_blank(),
      panel.grid = element_blank(),
      plot.margin = unit(rep(-1, 4), "cm")
    ) +
    coord_polar() +
    geom_bar(aes(x = as.factor(id), y = value, fill = group),
      data = data, stat = "identity"
    ) +

    # Add program labels
    geom_text(
      data = label_data2,
      aes(
        x = id, y = value + 10, label = stringr::str_wrap(individual, 20),
        lineheight = .75, hjust = hjust
      ),
      color = "black", alpha = 0.6, size = label_size,
      angle = label_data2$angle, inherit.aes = FALSE
    ) +

    # Add base line information
    geom_segment(
      data = base_data, aes(x = start, y = -5, xend = end, yend = -5),
      colour = "black", alpha = 0.8, size = 1, inherit.aes = FALSE
    ) +
    geom_text(
      data = base_data, aes(x = title, y = -20, label = group),
      colour = "black", alpha = 1, size = 6, fontface = "bold", inherit.aes = F
    ) +

    # Fill color
    scale_fill_manual(values = cols)

  if (nrow(label_dataNA) > 0) {
    p <- p + geom_text(
      data = label_dataNA,
      aes(
        x = id, y = value, label = stringr::str_wrap(individual, 30),
        lineheight = .75, hjust = hjust
      ),
      color = "black", alpha = 0.2, size = label_size,
      angle = label_dataNA$angle, inherit.aes = FALSE
    )
  }

  return(p)
}

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


# Get arguments, we only care for the first one
args <- commandArgs(trailingOnly = TRUE)
# Read-in tabular data from a csv file to create the visual
input_file <- args[[1]]
output_dir <- args[[2]]
data <- readr::read_csv(args[[1]])

# Generate radial plot based on the data
p <- ERAMRadialPlot(data)
png_file <- file.path(output_dir, "eram_visuals.png")
pdf_file <- file.path(output_dir, "eram_visuals.pdf")
# Save plot to png
ggplot2::ggsave(filename = png_file, plot = p, width = 8, height = 8)

# Save plot to pdf
ggplot2::ggsave(filename = pdf_file, plot = p, width = 8, height = 8)
