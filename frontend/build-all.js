import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function copyFolderRecursiveSync(source, target) {
  if (!fs.existsSync(target)) {
    fs.mkdirSync(target, { recursive: true });
  }

  if (fs.lstatSync(source).isDirectory()) {
    const files = fs.readdirSync(source);
    files.forEach((file) => {
      const curSource = path.join(source, file);
      const curTarget = path.join(target, file);
      if (fs.lstatSync(curSource).isDirectory()) {
        copyFolderRecursiveSync(curSource, curTarget);
      } else {
        fs.copyFileSync(curSource, curTarget);
      }
    });
  }
}

try {
  console.log('🚀 Step 1: Building Myntra My Picks MVP prototype...');
  const mvpPath = path.resolve(__dirname, '../docs/Blinkit_Cross_Sell_Growth/my-picks-mvp');
  
  console.log('Installing MVP dependencies...');
  execSync('npm install', { cwd: mvpPath, stdio: 'inherit' });
  
  console.log('Building MVP bundle...');
  execSync('npm run build', { cwd: mvpPath, stdio: 'inherit' });

  console.log('🚀 Step 2: Copying MVP assets into frontend public folder...');
  const sourceDist = path.join(mvpPath, 'dist');
  const targetPublic = path.resolve(__dirname, 'public/mypicks-mvp');

  if (fs.existsSync(targetPublic)) {
    fs.rmSync(targetPublic, { recursive: true, force: true });
  }
  
  copyFolderRecursiveSync(sourceDist, targetPublic);
  console.log('✓ MVP prototype assets successfully copied to public/mypicks-mvp');

  console.log('🚀 Step 3: Building main Pulse Intel dashboard...');
  execSync('npx vite build', { cwd: __dirname, stdio: 'inherit' });
  console.log('🎉 Unified build complete!');
} catch (error) {
  console.error('❌ Build failed:', error);
  process.exit(1);
}
