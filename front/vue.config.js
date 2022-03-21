const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  outputDir: 'dist/',
  assetsDir: 'assets/',
  devServer: {
    host: '0.0.0.0',
    port: 8000,
    disableHostCheck: true
  },
  transpileDependencies: [
    'vuetify'
  ],
  configureWebpack: {
    plugins: [new CompressionPlugin()]
  }
}
