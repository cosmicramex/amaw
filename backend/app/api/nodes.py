"""
Nodes API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.database.connection import get_db
from app.models.database import Node, Content
from datetime import datetime

router = APIRouter()

class NodeRequest(BaseModel):
    """Request model for node operations"""
    id: str
    type: str
    position_x: int
    position_y: int
    data: Optional[Dict[str, Any]] = {}

class NodeResponse(BaseModel):
    """Response model for node operations"""
    success: bool
    data: Dict[str, Any]
    message: str

class NodeListResponse(BaseModel):
    """Response model for node list"""
    success: bool
    nodes: List[Dict[str, Any]]
    message: str

@router.post("/create", response_model=NodeResponse)
async def create_node(
    request: NodeRequest,
    db: Session = Depends(get_db)
):
    """Create a new node"""
    try:
        # Check if node already exists
        existing_node = db.query(Node).filter(Node.id == request.id).first()
        if existing_node:
            raise HTTPException(status_code=400, detail="Node already exists")
        
        # Create new node
        node = Node(
            id=request.id,
            type=request.type,
            position_x=request.position_x,
            position_y=request.position_y,
            data=request.data
        )
        
        db.add(node)
        db.commit()
        db.refresh(node)
        
        return NodeResponse(
            success=True,
            data={
                "id": node.id,
                "type": node.type,
                "position_x": node.position_x,
                "position_y": node.position_y,
                "data": node.data,
                "created_at": node.created_at.isoformat() if node.created_at else None
            },
            message="Node created successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=NodeListResponse)
async def list_nodes(db: Session = Depends(get_db)):
    """Get all nodes"""
    try:
        nodes = db.query(Node).all()
        
        node_list = []
        for node in nodes:
            node_list.append({
                "id": node.id,
                "type": node.type,
                "position_x": node.position_x,
                "position_y": node.position_y,
                "data": node.data,
                "created_at": node.created_at.isoformat() if node.created_at else None,
                "updated_at": node.updated_at.isoformat() if node.updated_at else None
            })
        
        return NodeListResponse(
            success=True,
            nodes=node_list,
            message="Nodes retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{node_id}", response_model=NodeResponse)
async def get_node(node_id: str, db: Session = Depends(get_db)):
    """Get a specific node"""
    try:
        node = db.query(Node).filter(Node.id == node_id).first()
        
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        
        return NodeResponse(
            success=True,
            data={
                "id": node.id,
                "type": node.type,
                "position_x": node.position_x,
                "position_y": node.position_y,
                "data": node.data,
                "created_at": node.created_at.isoformat() if node.created_at else None,
                "updated_at": node.updated_at.isoformat() if node.updated_at else None
            },
            message="Node retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: str,
    request: NodeRequest,
    db: Session = Depends(get_db)
):
    """Update a node"""
    try:
        node = db.query(Node).filter(Node.id == node_id).first()
        
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        
        # Update node properties
        node.type = request.type
        node.position_x = request.position_x
        node.position_y = request.position_y
        node.data = request.data
        node.updated_at = datetime.now()
        
        db.commit()
        db.refresh(node)
        
        return NodeResponse(
            success=True,
            data={
                "id": node.id,
                "type": node.type,
                "position_x": node.position_x,
                "position_y": node.position_y,
                "data": node.data,
                "created_at": node.created_at.isoformat() if node.created_at else None,
                "updated_at": node.updated_at.isoformat() if node.updated_at else None
            },
            message="Node updated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{node_id}")
async def delete_node(node_id: str, db: Session = Depends(get_db)):
    """Delete a node"""
    try:
        node = db.query(Node).filter(Node.id == node_id).first()
        
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        
        # Delete associated content
        db.query(Content).filter(Content.node_id == node_id).delete()
        
        # Delete node
        db.delete(node)
        db.commit()
        
        return {
            "success": True,
            "message": "Node deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{node_id}/content")
async def get_node_content(node_id: str, db: Session = Depends(get_db)):
    """Get content associated with a node"""
    try:
        content = db.query(Content).filter(Content.node_id == node_id).first()
        
        if not content:
            return {
                "success": True,
                "content": None,
                "message": "No content found for this node"
            }
        
        return {
            "success": True,
            "content": {
                "id": content.id,
                "node_id": content.node_id,
                "source_url": content.source_url,
                "platform": content.platform,
                "title": content.title,
                "description": content.description,
                "thumbnail_url": content.thumbnail_url,
                "metadata": content.metadata,
                "content_text": content.content_text,
                "created_at": content.created_at.isoformat() if content.created_at else None
            },
            "message": "Content retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
