import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    // During development, proxy API requests to the FastAPI backend
    server: {
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            }
        }
    },
    build: {
        // Configure the build output
        outDir: '../app/static',
        emptyOutDir: true,
        sourcemap: true,
        // Output format for better integration with our server-side template
        rollupOptions: {
            output: {
                entryFileNames: 'js/[name].js',
                chunkFileNames: 'js/[name].js',
                assetFileNames: (assetInfo) => {
                    const ext = assetInfo.name?.split('.').pop()?.toLowerCase()
                    if (ext === 'css') {
                        return 'css/[name][extname]'
                    }
                    return 'assets/[name][extname]'
                }
            }
        }
    }
})
