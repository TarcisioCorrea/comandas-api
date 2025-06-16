# GUSTAVO PAES DE LIZ

from pydantic import BaseModel

class FuncionarioLogin(BaseModel):
    cpf: str
    senha: str

class Funcionario(BaseModel):
    id_funcionario: int = None
    nome: str
    matricula: str
    cpf: str
    telefone: str = None
    grupo: int
    senha: str = None