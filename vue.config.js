module.exports = {
  transpileDependencies: [],
  devServer: {
    port: 8080,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
        secure: false,
        logLevel: 'debug'
      }
    }
  }
}
