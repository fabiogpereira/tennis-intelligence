param(
    [string]$Commit = "83733587353df8a41f2fd4f516147d5aa83f5a8d",
    [string]$Destination = "data/raw/sackmann_archive"
)

$ErrorActionPreference = "Stop"

if (Test-Path -LiteralPath $Destination) {
    throw "Destination already exists: $Destination. Refusing to overwrite a source snapshot."
}

$parent = Split-Path -Parent $Destination
if ($parent) {
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
}

git init $Destination | Out-Null
git -C $Destination remote add origin https://github.com/Aneeshers/tennis-sackmann-archive.git
git -C $Destination fetch --depth 1 origin $Commit
git -C $Destination checkout --detach FETCH_HEAD | Out-Null

$actualCommit = git -C $Destination rev-parse HEAD
if ($actualCommit -ne $Commit) {
    throw "Expected context mirror commit $Commit but checked out $actualCommit"
}

Write-Output "Sackmann context mirror ready at $Destination"
Write-Output "commit=$actualCommit"
