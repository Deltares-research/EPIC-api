#! /usr/bin/Rscript

# Install requred R packages (if not already installed)
def_repo <- "http://cran.us.r-project.org"
if (!require(scales)) install.packages("scales", repos = def_repo)
if (!require(ggplot2)) install.packages("ggplot2", repos = def_repo)
if (!require(dplyr)) install.packages("dplyr", repos = def_repo)
if (!require(readr)) install.packages("readr", repos = def_repo)
if (!require(stringr)) install.packages("stringr", repos = def_repo)
if (!require(cowplot)) install.packages("cowplot", repos = def_repo)
if (!require(RColorBrewer)) install.packages("RColorBrewer", repos = def_repo)

################################################################################
# ERAM RADIAL PLOT FUNCTION

# Updated ERAM Radial Plot Function with Side Box Chart

ERAMRadialPlot <- function(data.to.plot,
                           empty_bar = 2,
                           ymin = -60, ymax = 140,
                           label_size = 2,
                           theme_colors = c("E" = '#fec44f', "P" = '#377eb8',
                                            "I" = '#4daf4a', "C" = '#984ea3',
                                            "R" = '#ff7f00'),
                           individuals_to_merge_E = c("Local Government", "Public & Stakeholder Engagement",
                                                      "Social Inclusion", "Education & Risk Communication",
                                                      "Scientific Collaboration", "Open Data"),
                           output_file = NULL) {
  
  require(scales)
  require(ggplot2)
  require(dplyr)
  require(stringr)
  require(cowplot)

# Trim whitespace from 'individual' and convert to character
data.to.plot <- data.to.plot %>%
  mutate(individual = trimws(as.character(individual)))
  
  # Keep a copy of original data for barplot
  data_original <- data.to.plot
  
  # --- Merge specified individuals in group 'E' for radial plot ---
  if (length(individuals_to_merge_E) > 0) {
    data.to.plot$individual <- as.character(data.to.plot$individual)
    
    mean_E <- data.to.plot %>%
      filter(group == "E", individual %in% individuals_to_merge_E) %>%
      summarize(value = mean(value), .groups = "drop") %>%
      mutate(group = "E", individual = "Whole of Society")
    
    data.to.plot <- data.to.plot %>%
      filter(!(group == "E" & individual %in% individuals_to_merge_E)) %>%
      bind_rows(mean_E)
    
    data.to.plot <- droplevels(data.to.plot)
  }
  
  # -----------------
  # RADIAL PLOT
  # -----------------
  prog_levels <- data.to.plot$individual
  
  data.template <- data.to.plot %>%
    mutate(group = factor(group, levels = c("P", "I", "C", "R", "E")),
           individual = factor(individual, levels = prog_levels)) %>%
    arrange(group) %>%
    mutate(value = 0)
  
  data2 <- data.to.plot %>%
    mutate(group = factor(group, levels = c("P", "I", "C", "R", "E")),
           individual = factor(individual, levels = prog_levels)) %>%
    arrange(group) %>%
    filter(value > 0) %>%
    mutate(value = scales::rescale(value, to = c(20, 80)))
  
  mindex <- which(data.template$individual %in% data2$individual)
  data.template$value[mindex] <- data2$value
  
  to_add <- data.frame(matrix(NA, empty_bar * nlevels(data.template$group), ncol(data.template)))
  colnames(to_add) <- colnames(data.template)
  to_add$group <- rep(levels(data.template$group), each = empty_bar)
  data.template <- rbind(data.template, to_add)
  data.template <- data.template %>% arrange(group)
  data.template$id <- seq(1, nrow(data.template))
  
  label_data <- data.template
  number_of_bar <- nrow(label_data)
  angle <- 90 - 360 * (label_data$id - 0.5) / number_of_bar
  label_data$hjust <- ifelse(angle < -90, 1, 0)
  label_data$angle <- ifelse(angle < -90, angle + 180, angle)
  
  base_data <- data.template %>%
    group_by(group) %>%
    summarize(start = min(id), end = max(id) - empty_bar, .groups = "drop") %>%
    rowwise() %>%
    mutate(title = mean(c(start, end)))
  
  grid_data <- base_data
  grid_data$end <- grid_data$end[c(nrow(grid_data), 1:(nrow(grid_data) - 1))] + 1
  grid_data$start <- grid_data$start - 1
  grid_data <- grid_data[-1,]
  
  label_data2 <- filter(label_data, value > 0)
  label_dataNA <- filter(label_data, value == 0)
  
  p_radial <- ggplot(data.template, aes(x = as.factor(id), y = value, fill = group)) +
    geom_bar(aes(x = as.factor(id), y = value),
             fill = "gray", stat = "identity", alpha = 0.8) +
    geom_segment(data = grid_data, aes(x = end, y = 80, xend = start, yend = 80),
                 colour = "grey50", size = 0.5, inherit.aes = FALSE) +
    geom_segment(data = grid_data, aes(x = end, y = 60, xend = start, yend = 60),
                 colour = "grey50", size = 0.5, inherit.aes = FALSE) +
    geom_segment(data = grid_data, aes(x = end, y = 40, xend = start, yend = 40),
                 colour = "grey50", size = 0.5, inherit.aes = FALSE) +
    geom_segment(data = grid_data, aes(x = end, y = 20, xend = start, yend = 20),
                 colour = "grey50", size = 0.5, inherit.aes = FALSE) +
    annotate("text", x = rep(max(data.template$id), 5), y = c(0, 20, 40, 60, 80),
             label = c("0", "1", "2", "3", "4"), color = "grey50", size = 5,
             fontface = "bold", hjust = 1) +
    ylim(ymin, ymax) +
    theme_minimal() +
    theme(
      legend.position = "none",
      axis.text = element_blank(),
      axis.title = element_blank(),
      panel.grid = element_blank(),
      plot.margin = margin(0, 0, 0, 0, "cm")
    ) +
    coord_polar() +
    geom_bar(aes(x = as.factor(id), y = value, fill = group),
             data = data.template, stat = "identity") +
    geom_bar(
      data = filter(data.template, individual == "Whole of Society"),
      aes(x = as.factor(id), y = value),
      stat = "identity",
      fill = "#fca636", color = NA
    ) +
    geom_text(data = label_data2,
              aes(x = id, y = value + 10, label = stringr::str_wrap(individual, 20),
                  lineheight = .75, hjust = hjust),
              color = "black", alpha = 0.6, size = label_size,
              angle = label_data2$angle, inherit.aes = FALSE) +
    geom_segment(data = base_data, aes(x = start, y = -5, xend = end, yend = -5),
                 colour = "black", size = 1, inherit.aes = FALSE) +
    geom_text(data = base_data, aes(x = title, y = -20, label = group),
              colour = "black", size = 6, fontface = "bold", inherit.aes = FALSE) +
    scale_fill_manual(values = theme_colors)
  
  if (nrow(label_dataNA) > 0) {
    p_radial <- p_radial + geom_text(data = label_dataNA,
                                     aes(x = id, y = value, label = stringr::str_wrap(individual, 30),
                                         lineheight = .75, hjust = hjust),
                                     color = "black", alpha = 0.2, size = label_size,
                                     angle = label_dataNA$angle, inherit.aes = FALSE)
  }
  
  # -----------------
  # WHOLE OF SOCIETY BARPLOT
  # -----------------
  subset_data <- data_original %>%
    filter(group == "E", individual %in% individuals_to_merge_E) %>%
    arrange(value)
  
  p_bar <- ggplot(subset_data, aes(x = value, y = reorder(individual, value))) +
    geom_col(fill = "#fca636") +
    theme_minimal() +
    theme(
      panel.grid.major.y = element_blank(),
      panel.grid.minor = element_blank(),
      axis.title = element_blank(),
      plot.margin = margin(5,5,5,5)
    ) +
    scale_x_continuous(
      limits = c(0, 4),
      breaks = 0:4,
      labels = c("N/A","Nascent","Engaged","Capable","Effective"),
      expand = c(0,0)
    ) +
    ggtitle("Whole of Society breakdown")
  
 # Adjust barplot dimensions
  p_bar <- p_bar + 
    scale_y_discrete(expand = c(0, 0))+
    coord_fixed(ratio = 0.5)
  
  p_bar <- p_bar + theme(plot.margin = margin(0.1, 0.1, 0.1, 0.6, "cm"))
  p_radial <- p_radial + theme(plot.margin = margin(0.1,0.1,0.1,0.1, "cm"))
  
  # Combine side by side using cowplot
  
  combined_plot <- ggdraw() +
    draw_plot(p_bar, x = 0, y = 0, width = 0.37, height = 1) +
    draw_plot(p_radial, x = 0.3, y = 0, width = 0.7, height = 1)
  
 
  if (!is.null(output_file)) {
    ggsave(output_file, combined_plot, width = 15, height = 8, dpi = 300)
  }
  
  return(combined_plot)
}


################################################################################


# Get arguments, we only care for the first one
args <- commandArgs(trailingOnly = TRUE)
# Read-in tabular data from a csv file to create the visual
input_file <- args[[1]]
output_dir <- args[[2]]
data <- readr::read_csv(args[[1]])

# Generate radial plot based on the data
p <- ERAMRadialPlot(data)

# Save plot to png
png_file <- file.path(output_dir, "eram_visuals.png")
ggplot2::ggsave(filename = png_file, plot = p, width = 8, height = 8)

# Save plot to pdf
pdf_file <- file.path(output_dir, "eram_visuals.pdf")
ggplot2::ggsave(filename = pdf_file, plot = p, width = 8, height = 8)

