const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Building Gaming Bot Desktop App...\n');

// Step 1: Build the React app
console.log('📦 Building React app...');
try {
  execSync('npm run build', { stdio: 'inherit' });
  console.log('✅ React build completed\n');
} catch (error) {
  console.error('❌ React build failed:', error.message);
  process.exit(1);
}

// Step 2: Copy Electron main process to dist
console.log('📁 Copying Electron files...');
const distPath = path.join(__dirname, '../dist');
if (!fs.existsSync(distPath)) {
  fs.mkdirSync(distPath);
}

try {
  fs.copyFileSync(
    path.join(__dirname, '../public/electron.js'),
    path.join(distPath, 'electron.js')
  );
  console.log('✅ Electron files copied\n');
} catch (error) {
  console.error('❌ Failed to copy Electron files:', error.message);
  process.exit(1);
}

// Step 3: Build Electron app
console.log('🔧 Building Electron executable...');
try {
  execSync('npx electron-builder --config electron-builder.json', { 
    stdio: 'inherit',
    env: {
      ...process.env,
      NODE_ENV: 'production'
    }
  });
  console.log('✅ Electron build completed');
  console.log('\n🎉 Gaming Bot Desktop App ready in dist-electron/ folder!');
} catch (error) {
  console.error('❌ Electron build failed:', error.message);
  process.exit(1);
}