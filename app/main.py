from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base
from app.api import leads, landing_pages, whatsapp, proposals
from app import models
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Lead Capture Platform with Territorial Intelligence",
    description="MVP - Platform for automated lead capture with WhatsApp integration and AI agent",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(leads.router)
app.include_router(landing_pages.router)
app.include_router(whatsapp.router)
app.include_router(proposals.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint"""
    return """
    <html>
        <head>
            <title>Lead Capture Platform</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #1a472a;
                }
                .feature {
                    margin: 20px 0;
                    padding: 15px;
                    background: #f9f9f9;
                    border-left: 4px solid #1a472a;
                }
                a {
                    color: #1a472a;
                    text-decoration: none;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Lead Capture Platform</h1>
                <p>MVP - Plataforma de Captação de Leads com Inteligência Territorial</p>
                
                <div class="feature">
                    <h3>✨ Features</h3>
                    <ul>
                        <li>Landing pages segmentadas por bairro</li>
                        <li>Integração bidirecional com WhatsApp</li>
                        <li>Agente de IA para qualificação de leads</li>
                        <li>Geração de propostas com aceite</li>
                        <li>Follow-up multimídia com urgência</li>
                        <li>Painel administrativo</li>
                        <li>Rastreamento de origem de leads</li>
                    </ul>
                </div>
                
                <div class="feature">
                    <h3>📚 API Documentation</h3>
                    <p><a href="/docs">Interactive API Docs (Swagger UI)</a></p>
                    <p><a href="/redoc">Alternative API Docs (ReDoc)</a></p>
                </div>
                
                <div class="feature">
                    <h3>🎯 Quick Links</h3>
                    <p><a href="/admin">Admin Dashboard</a></p>
                    <p><a href="/api/leads/stats/analytics">Lead Analytics</a></p>
                </div>
            </div>
        </body>
    </html>
    """


@app.get("/lp/{slug}", response_class=HTMLResponse)
async def render_landing_page(slug: str, request: Request):
    """Render landing page by slug"""
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        # Get landing page
        page = db.query(models.LandingPage).filter(
            models.LandingPage.slug == slug,
            models.LandingPage.is_active == True
        ).first()
        
        if not page:
            return HTMLResponse(content="<h1>Landing page not found</h1>", status_code=404)
        
        # Render template
        return templates.TemplateResponse(
            f"{page.template_name}.html",
            {
                "request": request,
                "page": page,
                "data": page.template_data or {}
            }
        )
    finally:
        db.close()


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Admin dashboard"""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial, sans-serif; background: #f5f5f5; }
            .header {
                background: #1a472a;
                color: white;
                padding: 20px;
                text-align: center;
            }
            .container {
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .stat-card h3 {
                color: #666;
                font-size: 14px;
                margin-bottom: 10px;
            }
            .stat-card .number {
                font-size: 36px;
                font-weight: bold;
                color: #1a472a;
            }
            .section {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .section h2 {
                color: #1a472a;
                margin-bottom: 15px;
            }
            .btn {
                background: #1a472a;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin: 5px;
            }
            .btn:hover {
                background: #2d5f3d;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background: #f9f9f9;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Admin Dashboard</h1>
            <p>Lead Capture Platform - Painel Administrativo</p>
        </div>
        
        <div class="container">
            <div class="stats" id="stats">
                <div class="stat-card">
                    <h3>Total de Leads</h3>
                    <div class="number" id="total-leads">-</div>
                </div>
                <div class="stat-card">
                    <h3>Novos Leads</h3>
                    <div class="number" id="new-leads">-</div>
                </div>
                <div class="stat-card">
                    <h3>Qualificados</h3>
                    <div class="number" id="qualified-leads">-</div>
                </div>
                <div class="stat-card">
                    <h3>Convertidos</h3>
                    <div class="number" id="converted-leads">-</div>
                </div>
            </div>
            
            <div class="section">
                <h2>⚡ Ações Rápidas</h2>
                <a href="/docs" class="btn">📚 API Docs</a>
                <a href="/api/leads/stats/analytics" class="btn">📈 Analytics</a>
                <button class="btn" onclick="loadLeads()">🔄 Atualizar Leads</button>
            </div>
            
            <div class="section">
                <h2>👥 Leads Recentes</h2>
                <div id="leads-table">
                    <p>Carregando...</p>
                </div>
            </div>
        </div>
        
        <script>
            async function loadStats() {
                try {
                    const response = await fetch('/api/leads/stats/analytics');
                    const data = await response.json();
                    
                    document.getElementById('total-leads').textContent = data.total_leads;
                    document.getElementById('new-leads').textContent = data.new_leads;
                    document.getElementById('qualified-leads').textContent = data.qualified_leads;
                    document.getElementById('converted-leads').textContent = data.converted_leads;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }
            
            async function loadLeads() {
                try {
                    const response = await fetch('/api/leads/?limit=20');
                    const leads = await response.json();
                    
                    let html = '<table><thead><tr><th>ID</th><th>Nome</th><th>Telefone</th><th>Bairro</th><th>Status</th><th>Temperatura</th><th>Origem</th></tr></thead><tbody>';
                    
                    leads.forEach(lead => {
                        html += `<tr>
                            <td>${lead.id}</td>
                            <td>${lead.name || 'N/A'}</td>
                            <td>${lead.phone}</td>
                            <td>${lead.neighborhood || 'N/A'}</td>
                            <td>${lead.status}</td>
                            <td>${lead.temperature}</td>
                            <td>${lead.source}</td>
                        </tr>`;
                    });
                    
                    html += '</tbody></table>';
                    document.getElementById('leads-table').innerHTML = html;
                } catch (error) {
                    console.error('Error loading leads:', error);
                    document.getElementById('leads-table').innerHTML = '<p>Erro ao carregar leads</p>';
                }
            }
            
            // Load data on page load
            loadStats();
            loadLeads();
            
            // Auto refresh every 30 seconds
            setInterval(() => {
                loadStats();
                loadLeads();
            }, 30000);
        </script>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
