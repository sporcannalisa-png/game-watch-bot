const { spawn } = require('child_process');
const path = require('path');

// Start Vite dev server
const vite = spawn('npm', ['run', 'dev'], {
  stdio: 'inherit',
  shell: true
});

// Wait for Vite to start, then launch Electron
setTimeout(() => {
  const electron = spawn('npx', ['electron', 'public/electron.js'], {
    stdio: 'inherit',
    shell: true,
    env: {
      ...process.env,
      NODE_ENV: 'development'
    }
  });

  electron.on('close', () => {
    vite.kill();
    process.exit();
  });
}, 3000);

process.on('SIGTERM', () => {
  vite.kill();
  process.exit();
});

process.on('SIGINT', () => {
  vite.kill();
  process.exit();
});