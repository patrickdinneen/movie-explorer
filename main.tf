variable "project_id" {
  default = "pjd-hosting"
}

variable "region" {
  default = "us-central1"
}

variable zone {
  default = "us-central1-c"
}

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.19.0"
    }
  }

  backend "gcs" {
    bucket = "pjd-hosting-tf"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_storage_bucket" "function_bucket" {
  name = "${var.project_id}-function"
  uniform_bucket_level_access = true
  location = var.region
}

data "archive_file" "similar_movies_function" {
  type = "zip"
  source_dir = "functions/similar_movies"
  output_path = "/tmp/similar_movies.zip"
}

resource "google_storage_bucket_object" "similar_movies_zip" {
  bucket = google_storage_bucket.function_bucket.name
  source = data.archive_file.similar_movies_function.output_path
  content_type = "application/zip"
  name = "src-similar-movies-${data.archive_file.similar_movies_function.output_md5}.zip"
}

resource "google_cloudfunctions_function" "similar_movies_function" {
  name = "similar-movies"
  runtime = "python37"
  entry_point = "echo"

  available_memory_mb = 256
  source_archive_bucket = google_storage_bucket.function_bucket.name
  source_archive_object = google_storage_bucket_object.similar_movies_zip.name
  trigger_http = true
}