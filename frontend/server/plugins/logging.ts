import { appendFileSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { consola } from 'consola'

export default defineNitroPlugin((nitroApp) => {
  const logPath = join(process.cwd(), '../conductor/frontend.log')
  
  // Ensure directory exists
  mkdirSync(dirname(logPath), { recursive: true })

  // Add a custom reporter to consola to mirror logs to a file
  consola.addReporter({
    log(logObj) {
      const date = new Date().toISOString()
      const level = logObj.type.toUpperCase()
      const message = logObj.args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg, null, 2) : arg
      ).join(' ')
      
      const logLine = `[${date}] [${level}] ${message}
`
      
      try {
        appendFileSync(logPath, logLine)
      } catch (err) {
        // Fallback to basic console if file write fails to avoid infinite loops
        process.stderr.write(`Failed to write to log file: ${err}
`)
      }
    }
  })

  consola.info(`Frontend logging initialized. Writing to: ${logPath}`)
})
