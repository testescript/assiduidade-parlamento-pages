#!/usr/bin/env python3
"""
Script para exportar dados da base de dados SQLite para JSON estáticos
para uso no GitHub Pages (sem backend)
"""

import json
import sys
import os
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from models import get_engine_and_session, Deputado, Sessao, Assiduidade, DeputadoAtividade, AgendaItem
from sqlalchemy import func

def exportar_deputados(session):
    """Exporta dados de deputados com métricas de assiduidade"""
    print("📊 Exportando deputados...")
    
    deputados = session.query(Deputado).all()
    resultado = []
    
    for dep in deputados:
        # Calcular métricas
        assiduidades = session.query(Assiduidade).filter(
            Assiduidade.deputado_id == dep.id
        ).all()
        
        # Usar comparação parcial para status (pode ser "P" ou "Presença (P)")
        presencas = sum(1 for a in assiduidades if 'P)' in a.status or a.status == 'Presença (P)')
        faltas_penalizadoras = sum(1 for a in assiduidades if 'Quórum' in a.status or a.status == 'Falta ao Quórum de Votação')
        faltas_justificadas = sum(1 for a in assiduidades if 'FJ)' in a.status or a.status == 'Falta Justificada (FJ)')
        missao_parlamentar = sum(1 for a in assiduidades if 'AMP)' in a.status or a.status == 'Ausência em Missão Parlamentar (AMP)')
        
        total_base = presencas + faltas_penalizadoras
        assiduidade_pct = round((presencas / total_base * 100), 2) if total_base > 0 else 0
        
        # IMPORTANTE: Só exportar deputados que têm pelo menos 1 registo de assiduidade
        if len(assiduidades) > 0:
            resultado.append({
                'id': dep.id,
                'nome': dep.nome_original_ultimo,
                'partido': dep.partido_atual,
                'presencas': presencas,
                'faltas_justificadas': faltas_justificadas,
                'missao_parlamentar_amp': missao_parlamentar,
                'faltas_penalizadoras': faltas_penalizadoras,
                'assiduidade_pct': assiduidade_pct
            })
    
    print(f"   ✅ {len(resultado)} deputados com registos de assiduidade")
    return {'ok': True, 'deputados': resultado}

def exportar_sessoes(session):
    """Exporta dados de sessões"""
    print("📅 Exportando sessões...")
    
    sessoes = session.query(Sessao).all()
    resultado = []
    
    for s in sessoes:
        resultado.append({
            'id': s.id,
            'legislatura': s.legislatura,
            'numero': s.numero,
            'tipo': s.tipo,
            'data': s.data.isoformat() if s.data else None,
            'id_legis_sessao': s.id_legis_sessao
        })
    
    return {'ok': True, 'sessoes': resultado}

def exportar_estatisticas_sessoes(session):
    """Exporta estatísticas agregadas por sessão"""
    print("📈 Exportando estatísticas de sessões...")
    
    sessoes = session.query(Sessao).all()
    resultado = []
    
    for s in sessoes:
        assiduidades = session.query(Assiduidade).filter(
            Assiduidade.sessao_id == s.id
        ).all()
        
        presencas = sum(1 for a in assiduidades if 'P)' in a.status or a.status == 'Presença (P)')
        faltas_penalizadoras = sum(1 for a in assiduidades if 'Quórum' in a.status)
        
        total_base = presencas + faltas_penalizadoras
        assiduidade_pct = round((presencas / total_base * 100), 2) if total_base > 0 else 0
        
        resultado.append({
            'sessao_id': s.id,
            'legislatura': s.legislatura,
            'numero': s.numero,
            'tipo': s.tipo,
            'data': s.data.isoformat() if s.data else None,
            'presencas': presencas,
            'faltas': faltas_penalizadoras,
            'assiduidade_pct': assiduidade_pct
        })
    
    return {'ok': True, 'sessoes': resultado}

def exportar_atividades(session):
    """Exporta atividades parlamentares"""
    print("🗂️ Exportando atividades...")
    
    atividades = session.query(DeputadoAtividade).all()
    resultado = []
    
    for ativ in atividades:
        deputado = session.query(Deputado).filter(Deputado.id == ativ.deputado_id).first()
        
        resultado.append({
            'id': ativ.id,
            'deputado_id': ativ.deputado_id,
            'deputado_nome': deputado.nome_original_ultimo if deputado else None,
            'partido': deputado.partido_atual if deputado else None,
            'tipo': ativ.tipo,
            'legislatura': ativ.legislatura,
            'total': ativ.total,
            'ultima_data': ativ.ultima_data.isoformat() if ativ.ultima_data else None,
            'detalhes': ativ.detalhes
        })
    
    return {'ok': True, 'atividades': resultado}

def exportar_agenda(session):
    """Exporta agenda parlamentar"""
    print("📆 Exportando agenda...")
    
    # Limitar aos últimos 100 itens
    agenda = session.query(AgendaItem).order_by(AgendaItem.inicio.desc()).limit(100).all()
    resultado = []
    
    for item in agenda:
        resultado.append({
            'id': item.id,
            'inicio': item.inicio.isoformat() if item.inicio else None,
            'fim': item.fim.isoformat() if item.fim else None,
            'titulo': item.titulo,
            'link': item.link
        })
    
    return {'ok': True, 'agenda': resultado}

def exportar_substituicoes(session):
    """Exporta dados de substituições (placeholder)"""
    print("🔄 Exportando substituições...")
    return {'ok': True, 'substituicoes': []}

def main():
    print("🚀 Iniciando exportação de dados para JSON...")
    
    # Configurar caminho de saída
    output_dir = Path(__file__).parent / 'data'
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Diretório de saída: {output_dir}\n")
    
    # Conectar à BD
    engine, SessionLocal = get_engine_and_session()
    session = SessionLocal()
    
    try:
        # Exportar cada tipo de dados
        arquivos = {
            'deputados.json': exportar_deputados(session),
            'sessoes.json': exportar_sessoes(session),
            'estatisticas_sessoes.json': exportar_estatisticas_sessoes(session),
            'atividades.json': exportar_atividades(session),
            'agenda.json': exportar_agenda(session),
            'substituicoes.json': exportar_substituicoes(session)
        }
        
        # Salvar cada arquivo
        print()
        for filename, data in arquivos.items():
            filepath = output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Mostrar tamanho do arquivo
            size = filepath.stat().st_size
            size_kb = size / 1024
            print(f"✅ {filename} - {size_kb:.1f} KB")
        
        print(f"\n🎉 Exportação concluída! {len(arquivos)} arquivos criados.")
        
    finally:
        session.close()

if __name__ == '__main__':
    main()
