

# Node.js Windows 安装指南

最简单的方法是直接从官网下载和安装。以下是三种方式：

## 方法 1: 直接下载安装（推荐）

1. 访问 https://nodejs.org/
2. 点击绿色的 "LTS" 按钮（推荐版本）
3. 下载 Windows Installer (.msi) 文件
4. 双击运行安装程序
5. 按照提示完成安装（保持默认设置即可）
6. 安装完成后，重启 PowerShell 或 CMD
7. 验证安装：
   ```powershell
   node --version
   npm --version
   ```

## 方法 2: 使用 Chocolatey（需要已安装 Chocolatey）

如果你的电脑上已经安装了 Chocolatey 包管理器，可以运行：

```powershell
# 以管理员身份运行 PowerShell，然后执行：
choco install nodejs -y
```

## 方法 3: 使用 NVM (Node Version Manager)

NVM 允许你安装和切换多个 Node.js 版本：

1. 访问 https://github.com/coreybutler/nvm-windows
2. 下载 nvm-setup.exe
3. 运行安装程序
4. 重启 PowerShell，运行：
   ```powershell
   nvm install latest
   nvm use latest
   ```

## 验证安装

安装完成后，在 PowerShell 或 CMD 中运行：

```powershell
node --version
npm --version
```

应该看到类似的输出：
```
v20.x.x
9.x.x
```

如果看到版本号，说明安装成功！