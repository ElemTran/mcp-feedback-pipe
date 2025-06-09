module.exports = {
  // 基本格式化选项
  semi: true,
  singleQuote: true,
  quoteProps: 'as-needed',
  trailingComma: 'none',
  bracketSpacing: true,
  bracketSameLine: false,
  arrowParens: 'avoid',
  
  // 缩进和换行
  tabWidth: 2,
  useTabs: false,
  printWidth: 100,
  endOfLine: 'lf',
  
  // 特定文件类型配置
  overrides: [
    {
      files: '*.js',
      options: {
        parser: 'babel'
      }
    }
  ]
};