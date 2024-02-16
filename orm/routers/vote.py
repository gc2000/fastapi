from fastapi import Depends, FastAPI, Response, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from .. import database, models, schemas, oauth2


router = APIRouter (
    prefix='/vote',
    tags = ['Vote']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):

    if db.query (models.Post).filter(models.Vote.post_id == vote.post_id).first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"post id {vote.post_id} not found")
    vote_query = db.query (models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.id} has already voted on post {vote.post_id}")
        new_vote = models.Vote(post_id = vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vote not found")

        vote_query.delete(synchronize_session=False)
        db.commit()
        
        return {"message":"successfully deleted vote"}