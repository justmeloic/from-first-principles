export interface BlogPost {
  id: string
  title: string
  author: string
  date: string
  thumbnail: string
  content: {
    simple: string
    detailed: string
  }
}
