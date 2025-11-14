from pathlib import Path

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# Base declarativa
Base = declarative_base()

def get_engine_and_session():
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "database" / "base.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    SessionLocal = sessionmaker(bind=engine)
    return engine, SessionLocal

# Modelos
class Deputado(Base):
    __tablename__ = "deputados"
    id = Column(Integer, primary_key=True)
    nome_normalizado = Column(String, unique=True, nullable=False)
    nome_original_ultimo = Column(String, nullable=False)
    partido_atual = Column(String, nullable=True)

    # Relação com assiduidade
    assiduidades = relationship("Assiduidade", back_populates="deputado")
    atividades = relationship("DeputadoAtividade", back_populates="deputado")

class Sessao(Base):
    __tablename__ = "sessoes"
    id = Column(Integer, primary_key=True)
    id_legis_sessao = Column(String, unique=True, nullable=False)
    legislatura = Column(String, nullable=False)
    numero = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    data = Column(Date, nullable=False)

    # Relação com assiduidade
    assiduidades = relationship("Assiduidade", back_populates="sessao")

class Assiduidade(Base):
    __tablename__ = "assiduidade"
    id = Column(Integer, primary_key=True)
    sessao_id = Column(Integer, ForeignKey("sessoes.id"), nullable=False)
    deputado_id = Column(Integer, ForeignKey("deputados.id"), nullable=False)
    partido = Column(String, nullable=True)
    status = Column(String, nullable=False)
    motivo = Column(String, nullable=True)

    # Relações
    sessao = relationship("Sessao", back_populates="assiduidades")
    deputado = relationship("Deputado", back_populates="assiduidades")

    # Constraint para evitar duplicados
    __table_args__ = (
        UniqueConstraint("sessao_id", "deputado_id", name="_sessao_deputado_uc"),
    )


class DeputadoAtividade(Base):
    __tablename__ = "deputado_atividades"
    id = Column(Integer, primary_key=True)
    deputado_id = Column(Integer, ForeignKey("deputados.id"), nullable=False)
    tipo = Column(String, nullable=False)
    legislatura = Column(String, nullable=True)
    total = Column(Integer, default=0, nullable=False)
    ultima_data = Column(Date, nullable=True)
    detalhes = Column(Text, nullable=True)

    deputado = relationship("Deputado", back_populates="atividades")

    __table_args__ = (
        UniqueConstraint(
            "deputado_id", "tipo", "legislatura", name="_deputado_tipo_legis_uc"
        ),
    )


class AgendaItem(Base):
    __tablename__ = "agenda_items"
    id = Column(Integer, primary_key=True)
    externo_id = Column(Integer, unique=True, nullable=False)
    titulo = Column(String, nullable=False)
    tema = Column(String, nullable=True)
    secao = Column(String, nullable=True)
    organizacao = Column(String, nullable=True)
    local = Column(String, nullable=True)
    leg_des = Column(String, nullable=True)
    parlamentar_group = Column(String, nullable=True)
    link = Column(String, nullable=True)
    inicio = Column(DateTime, nullable=True)
    fim = Column(DateTime, nullable=True)
    texto = Column(Text, nullable=True)


# Criar tabelas automaticamente se não existirem
engine, _ = get_engine_and_session()
Base.metadata.create_all(engine)
