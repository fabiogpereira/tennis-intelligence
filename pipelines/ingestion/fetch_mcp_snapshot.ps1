param(
    [string]$Commit = "2c59eef194967e688b69e73df344184a06322cd8",
    [string]$Destination = "data/raw/mcp_upstream"
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
git -C $Destination remote add origin https://github.com/JeffSackmann/tennis_MatchChartingProject.git
git -C $Destination fetch --depth 1 origin $Commit
git -C $Destination checkout --detach FETCH_HEAD | Out-Null

$actualCommit = git -C $Destination rev-parse HEAD
if ($actualCommit -ne $Commit) {
    throw "Expected MCP commit $Commit but checked out $actualCommit"
}

Write-Output "MCP snapshot ready at $Destination"
Write-Output "commit=$actualCommit"
