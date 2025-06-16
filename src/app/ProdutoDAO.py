# GUSTAVO PAES DE LIZ

from fastapi import APIRouter
from domain.entities.Produto import Produto
import db
from infra.orm.ProdutoModel import ProdutoDB
import base64

# import da segurança
from typing import Annotated
from fastapi import Depends
from security import get_current_active_user, User

# dependências de forma global
router = APIRouter( dependencies=[Depends(get_current_active_user)] )

def converter_base64_para_bytes(base64_string):
    if "," in base64_string:
        base64_data = base64_string.split(",")[1]
    else:
        base64_data = base64_string  # já é só base64 sem prefixo

    return base64.b64decode(base64_data)

def produto_to_dict(produto):
    # converte os bytes da imagem para base64 com prefixo
    if produto.foto:
        foto_base64 = base64.b64encode(produto.foto).decode("utf-8")
        mimetype = "image/jpeg"  # ou determine dinamicamente
        foto = f"data:{mimetype};base64,{foto_base64}"
    else:
        foto = None

    return {
        "id_produto": produto.id_produto,
        "nome": produto.nome,
        "descricao": produto.descricao,
        "foto": foto,
        "valor_unitario": produto.valor_unitario
    }

@router.get("/produto/", tags=["Produto"])
async def get_produto():
    try:
        session = db.Session()
        dados = session.query(ProdutoDB).all()

        # transforma todos os produtos em dicionário
        resultado = [produto_to_dict(p) for p in dados]

        return resultado, 200
    except Exception as e:
        return {"erro": str(e)}, 400
    finally:
        session.close()

@router.get("/produto/{id}", tags=["Produto"])
async def get_produto(id: int):
    try:
        session = db.Session()
        dados = session.query(ProdutoDB).filter(ProdutoDB.id_produto == id).first()

        if not dados:
            return {"erro": "Produto não encontrado"}, 404

        return produto_to_dict(dados), 200
    except Exception as e:
        return {"erro": str(e)}, 400
    finally:
        session.close()

@router.post("/produto/", tags=["Produto"])
async def post_produto(corpo: Produto):
    try:
        session = db.Session()

        if corpo.foto is not None:
            foto_bytes = converter_base64_para_bytes(corpo.foto)
        else:
            foto_bytes = None

        # cria um novo objeto com os dados da requisição
        dados = ProdutoDB(None, corpo.nome, corpo.descricao, foto_bytes, corpo.valor_unitario)

        session.add(dados)
        # session.flush()
        session.commit()

        return {"id": dados.id_produto}, 200
    except Exception as e:
        session.rollback()
        return {"erro": str(e)}, 400
    finally:
        session.close()

@router.put("/produto/{id}", tags=["Produto"])
async def put_produto(id: int, corpo: Produto):
    try:
        session = db.Session()

        # busca os dados atuais pelo id
        dados = session.query(ProdutoDB).filter(ProdutoDB.id_produto == id).one()

        # atualiza os dados com base no corpo da requisição
        dados.nome = corpo.nome
        dados.descricao = corpo.descricao
        if corpo.foto is not None:
            dados.foto = converter_base64_para_bytes(corpo.foto)
        dados.valor_unitario = corpo.valor_unitario
        
        session.add(dados)
        session.commit()

        return {"id": dados.id_produto}, 200
    except Exception as e:
        session.rollback()
        return {"erro": str(e)}, 400
    finally:
        session.close()

@router.delete("/produto/{id}", tags=["Produto"])
async def delete_produto(id: int):
    try:
        session = db.Session()
        
        # busca os dados atuais pelo id
        dados = session.query(ProdutoDB).filter(ProdutoDB.id_produto == id).one()

        session.delete(dados)
        session.commit()

        return {"id": dados.id_produto}, 200
    except Exception as e:
        session.rollback()
        return {"erro": str(e)}, 400
    finally:
        session.close()