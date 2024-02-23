@echo off

pushd %CD%
cd /D ..
mvn package && docker build -t otus-dz2-docker-health-0.0.1 . && POPD
