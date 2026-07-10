import ts from 'typescript'
import { readFileSync, writeFileSync, unlinkSync, readdirSync, statSync, rmSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const srcRoot = join(dirname(fileURLToPath(import.meta.url)), '..', 'src')

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name)
    if (statSync(path).isDirectory()) {
      if (name !== 'types') walk(path, out)
    } else if (/\.tsx?$/.test(name)) out.push(path)
  }
  return out
}

const files = walk(srcRoot)

for (const file of files) {
  let content = readFileSync(file, 'utf8')
  // Drop type-only imports and type definitions folder usage
  content = content.replace(/^import type .+;\r?\n/gm, '')
  content = content.replace(/import \{([^}]+)\} from ('[^']+');/g, (match, imports, from) => {
    const kept = imports.split(',').map((s) => s.trim()).filter((s) => s && !s.startsWith('type '))
    return kept.length ? `import { ${kept.join(', ')} } from ${from};` : ''
  })

  const isTsx = file.endsWith('.tsx')
  const js = ts.transpileModule(content, {
    compilerOptions: {
      jsx: isTsx ? ts.JsxEmit.Preserve : ts.JsxEmit.None,
      module: ts.ModuleKind.ESNext,
      target: ts.ScriptTarget.ES2020,
    },
    fileName: file,
  }).outputText

  const outFile = file.replace(/\.tsx$/, '.jsx').replace(/\.ts$/, '.js')
  writeFileSync(outFile, js, 'utf8')
  unlinkSync(file)
}

rmSync(join(srcRoot, 'types'), { recursive: true, force: true })
console.log(`Converted ${files.length} files to JavaScript.`)
