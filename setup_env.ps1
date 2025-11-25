# Setup Environment Variables for RAG Query
# Run this once per PowerShell session: .\setup_env.ps1

# Set Gemini API Key
$env:GOOGLE_API_KEY = "AIzaSyAa2vAQjxEFJMwowuN25BFbOTbjkfTn84U"

Write-Host "✓ Environment configured!" -ForegroundColor Green
Write-Host "  GOOGLE_API_KEY: $($env:GOOGLE_API_KEY.Substring(0,20))..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Ready to use RAG query:" -ForegroundColor Yellow
Write-Host "  python rag_query.py --query 'Your question here' --top-k 5" -ForegroundColor White
