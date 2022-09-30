#! /usr/bin/Rscript

# Install requred R packages (if not already installed)
def_repo <- "http://cran.us.r-project.org"
if (!require(scales)) install.packages("scales", repos = def_repo)
if (!require(ggplot2)) install.packages("ggplot2", repos = def_repo)
if (!require(dplyr)) install.packages("dplyr", repos = def_repo)
if (!require(readr)) install.packages("readr", repos = def_repo)
if (!require(stringr)) install.packages("stringr", repos = def_repo)
if (!require(RColorBrewer)) install.packages("RColorBrewer", repos = def_repo)

################################################################################
# ERAM RADIAL PLOT FUNCTION

ERAMRadialPlot <- function(data.to.plot = NULL,
                           empty_bar = 2,
                           ymin = -60,
                           ymax = 140,
                           label_size = 2,
                           group_levels = c("P", "I", "C", "R", "E"),
                           group_colors = NULL)

{

  require(scales)
  require(ggplot2)
  require(dplyr)
  require(RColorBrewer)

  # set group levels, program levels, and group colors
  if(is.null(group_levels)) group_levels <- unique(data.to.plot$group)
  group_colors <- setNames(colorRampPalette(brewer.pal(8, "Set2"))(length(group_levels)), group_levels)
  prog_levels <- unique(data.to.plot$individual)

  # Prepare data for plotting
  data.template <- data.to.plot %>%
    mutate(group = factor(group, levels = group_levels)) %>%
    mutate(individual = factor(individual, levels = prog_levels)) %>%
    arrange(group) %>%
    mutate(value = 0)

  data2 <- data.to.plot %>%
    mutate(group = factor(group, levels = group_levels)) %>%
    mutate(individual = factor(individual, levels = prog_levels)) %>%
    arrange(group) %>%
    filter(value > 0)

  # Rescale if there is nonzero values
  if(nrow(data2) > 0) data2$value = scales::rescale(data2$value, to = c(0, 80), from = c(0,4))

  mindex <- which(data.template$individual %in% data2$individual)
  data.template$value[mindex] <- data2$value

  # Set a number of 'empty bar' to add at the end of each group
  to_add <- data.frame(matrix(NA, empty_bar * nlevels(data.template$group), ncol(data.template)))
  colnames(to_add) <- colnames(data.template)
  to_add$group <- rep(levels(data.template$group), each = empty_bar)
  data.template <- rbind(data.template, to_add)
  data.template <- data.template %>% arrange(group)
  data.template$id <- seq(1, nrow(data.template))

  # Data frame to store the labels
  label_data <- data.template
  number_of_bar <- nrow(label_data)
  angle <- 90 - 360 * (label_data$id - 0.5) / number_of_bar
  label_data$hjust <- ifelse(angle < -90, 1, 0)
  label_data$angle <- ifelse(angle < -90, angle + 180, angle)

  # Data frame to store base lines
  base_data <- data.template %>%
    group_by(group) %>%
    summarize(start = min(id), end = max(id) - empty_bar) %>%
    rowwise() %>%
    mutate(title = mean(c(start, end)))

  # Data frame to store grids
  grid_data <- base_data
  grid_data$end <- grid_data$end[c(nrow(grid_data), 1:nrow(grid_data) - 1)] + 1
  grid_data$start <- grid_data$start - 1

  if(length(group_levels) > 1) grid_data <- grid_data[-1, ]

  label_data2 <- filter(label_data, value > 0)
  label_dataNA <- filter(label_data, value == 0)



  # Make the plot
  p <- ggplot(data.template, aes(x = as.factor(id), y = value, fill = group)) +

    # Set main bars
    geom_bar(aes(x = as.factor(id), y = value), fill = "gray", stat = "identity", alpha = 0.8) +

    # Set radial segments
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
    geom_segment(
      data = grid_data, aes(x = end, y = 0, xend = start, yend = 0),
      colour = "grey50", alpha = 1, size = 0.5, inherit.aes = F
    ) +

    # Set y-axis scales
    annotate("text",
      x = rep(max(data.template$id), 5), y = c(0, 20, 40, 60, 80),
      label = c("0", "1", "2", "3", "4"), color = "grey50", size = 5,
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
      data = data.template, stat = "identity"
    ) +

    {if (nrow(label_data2) > 0)
       # Add program labels
      geom_text(
        data = label_data2,
          aes(x = id, y = value + 10, label = stringr::str_wrap(individual, 20),
              lineheight = .75, hjust = hjust),
      color = "black", alpha = 0.6, size = label_size,
      angle = label_data2$angle, inherit.aes = FALSE)
    } +

    # Add base line information
    geom_segment(
      data = base_data, aes(x = start, y = -5, xend = end, yend = -5),
      colour = "black", alpha = 0.8, size = 1, inherit.aes = FALSE
    ) +
    geom_text(
      data = base_data, aes(x = title, y = -20, label = group),
      colour = "black", alpha = 1, size = 6, fontface = "bold", inherit.aes = F
    ) +

    scale_fill_manual(values = group_colors)

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

