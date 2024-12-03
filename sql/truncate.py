from sql.posts import Post
from sql.comment import Comment

post = Post()
comment = Comment()
post.truncate()
comment.truncate()