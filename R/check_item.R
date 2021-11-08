check_item <- function(...) {
  if (!("exams" %in% installed.packages()[ , "Package"])){
    install.packages("exams")
  }
  if (!("rstudioapi" %in% installed.packages()[ , "Package"])){
    install.packages("rstudioapi")
  }
  file = rstudioapi::getSourceEditorContext()$path
  exams::exams2html(file)
}
