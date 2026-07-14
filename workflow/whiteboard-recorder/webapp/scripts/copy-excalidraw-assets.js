import fs from 'fs/promises'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(__dirname, '..')

const sourceDir = path.join(root, 'node_modules', '@excalidraw', 'excalidraw', 'dist')
const targetDir = path.join(root, 'public')

const assetDirs = ['excalidraw-assets', 'excalidraw-assets-dev']

async function copyDir(src, dest) {
  await fs.mkdir(dest, { recursive: true })
  const entries = await fs.readdir(src, { withFileTypes: true })
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name)
    const destPath = path.join(dest, entry.name)
    if (entry.isDirectory()) {
      await copyDir(srcPath, destPath)
    } else {
      await fs.copyFile(srcPath, destPath)
    }
  }
}

async function main() {
  for (const dir of assetDirs) {
    const src = path.join(sourceDir, dir)
    const dest = path.join(targetDir, dir)
    try {
      await fs.access(src)
      await copyDir(src, dest)
      console.log(`Copied ${dir} to public/`)
    } catch (err) {
      if (err.code === 'ENOENT') {
        console.warn(`Source not found, skipped: ${src}`)
      } else {
        throw err
      }
    }
  }
}

main().catch(err => {
  console.error('Failed to copy Excalidraw assets:', err)
  process.exit(1)
})
