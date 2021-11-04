check_item <- function(...) {
  if (!("exams" %in% installed.packages()[ , "Package"])){
    install.packages("exams")
  }
  file = rstudioapi::getSourceEditorContext()$path
  exams::exams2html(file)
}
