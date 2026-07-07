import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

const worksDir = path.resolve(__dirname, '..', 'output')

function findWhiteboardFiles(dir: string): string[] {
  const results: string[] = []
  if (!fs.existsSync(dir)) return results
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      results.push(...findWhiteboardFiles(fullPath))
    } else if (entry.isFile() && entry.name.endsWith('.whiteboard.json')) {
      results.push(fullPath)
    }
  }
  return results
}

function worksMiddleware() {
  return {
    name: 'works-api',
    configureServer(server: any) {
      server.middlewares.use('/api/works', (req: any, res: any, next: any) => {
        if (req.method !== 'GET') return next()
        // connect mount 后 req.url 已去掉 /api/works 前缀
        const pathname = req.url || '/'

        if (pathname === '/list' || pathname === '/list/') {
          try {
            const files = findWhiteboardFiles(worksDir)
            const works = files.map(filePath => {
              const relPath = path.relative(worksDir, filePath).replace(/\\/g, '/')
              const stat = fs.statSync(filePath)
              const folder = path.dirname(relPath)
              let title = path.basename(relPath, '.whiteboard.json')
              try {
                const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'))
                if (data.title) title = data.title
              } catch {}
              return { id: relPath, title, folder, updatedAt: stat.mtime.toISOString() }
            })
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ works }))
          } catch (err: any) {
            res.statusCode = 500
            res.end(JSON.stringify({ error: err.message }))
          }
          return
        }

        const match = pathname.match(/^\/(.+)$/)
        if (match) {
          let relPath = decodeURIComponent(match[1]).replace(/\/$/, '')
          let filePath = path.join(worksDir, relPath)
          if (!filePath.startsWith(worksDir) || !fs.existsSync(filePath)) {
            res.statusCode = 404
            res.end(JSON.stringify({ error: 'Work not found' }))
            return
          }
          // 如果只传了目录名，自动查找目录下的第一个 .whiteboard.json 文件
          if (fs.statSync(filePath).isDirectory()) {
            const files = fs.readdirSync(filePath)
            const wbFile = files.find(f => f.endsWith('.whiteboard.json'))
            if (!wbFile) {
              res.statusCode = 404
              res.end(JSON.stringify({ error: 'No whiteboard file in work folder' }))
              return
            }
            filePath = path.join(filePath, wbFile)
          }
          res.setHeader('Content-Type', 'application/json')
          res.end(fs.readFileSync(filePath, 'utf-8'))
          return
        }

        next()
      })
    }
  }
}

export default defineConfig({
  plugins: [react(), worksMiddleware()],
  server: {
    port: 3000
  },
  define: {
    'process.env': {}
  }
})
