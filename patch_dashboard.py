import os

file_path = "templates/index.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Particle Class
old_particle = """    class Particle {
      constructor(x, y, vx, vy, color, life=25, size=4) {
        this.x = x; this.y = y; this.vx = vx; this.vy = vy;
        this.color = color; this.life = life; this.maxLife = life; this.size = size;
      }
      update() {
        this.x += this.vx; this.y += this.vy;
        this.vx *= 0.94; this.vy *= 0.94; this.vy += 0.15; // Gravity
        this.life--; return this.life > 0;
      }
      draw(ctx) {
        const alpha = this.life / this.maxLife;
        ctx.fillStyle = this.color;
        ctx.shadowBlur = 10 * alpha;
        ctx.shadowColor = this.color;
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * alpha, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1.0;
      }
    }"""

# Note: We need to be careful with indentation and exact string matching.
# Since the tool failed, I'll use a more flexible regex-based approach for the Particle class.

import re

# Replace Particle Class
particle_pattern = r"class Particle\s*\{.*?draw\(ctx\)\s*\{.*?\}\s*\}"
new_particle = """class Particle {
      constructor(x, y, vx, vy, color, life=35, size=5, type='circle') {
        this.x = x; this.y = y; this.vx = vx; this.vy = vy;
        this.color = color;
        this.life = life;
        this.maxLife = life;
        this.size = size;
        this.type = type;
        this.angle = Math.random() * Math.PI * 2;
        this.rotSpeed = (Math.random() - 0.5) * 0.2;
      }
      update() {
        this.x += this.vx; this.y += this.vy;
        this.angle += this.rotSpeed;
        this.vx *= 0.98;
        this.vy *= 0.98;
        this.vy += 0.22; // Gravity for falling effect
        this.life--; return this.life > 0;
      }
      draw(ctx) {
        const alpha = this.life / this.maxLife;
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);
        ctx.fillStyle = this.color;
        ctx.shadowBlur = 15 * alpha;
        ctx.shadowColor = this.color;
        ctx.globalAlpha = alpha;
        
        if (this.type === 'star') {
          this.drawStar(ctx, 0, 0, 5, this.size * alpha * 1.5, this.size * alpha * 0.6);
        } else {
          ctx.beginPath();
          ctx.arc(0, 0, this.size * alpha, 0, Math.PI * 2);
          ctx.fill();
        }
        
        ctx.restore();
        ctx.globalAlpha = 1.0;
        ctx.shadowBlur = 0;
      }
      drawStar(ctx, cx, cy, spikes, outerRadius, innerRadius) {
        let rot = Math.PI / 2 * 3;
        let x = cx;
        let y = cy;
        let step = Math.PI / spikes;
        ctx.beginPath();
        ctx.moveTo(cx, cy - outerRadius);
        for (let i = 0; i < spikes; i++) {
          x = cx + Math.cos(rot) * outerRadius;
          y = cy + Math.sin(rot) * outerRadius;
          ctx.lineTo(x, y);
          rot += step;
          x = cx + Math.cos(rot) * innerRadius;
          y = cy + Math.sin(rot) * innerRadius;
          ctx.lineTo(x, y);
          rot += step;
        }
        ctx.lineTo(cx, cy - outerRadius);
        ctx.closePath();
        ctx.fill();
      }
    }"""

content = re.sub(particle_pattern, new_particle, content, flags=re.DOTALL)

# 2. Update HUD (Stability and Finger Count)
content = content.replace("STABILITY: STANDBY", "STABILITY: ONLINE")
if "`FINGER COUNT:" not in content:
    content = content.replace("STABILITY: ONLINE", "FINGER COUNT: ${currentFingerCount}`, px + 15, py + 180);\\n\\n      ctx.fillStyle = \\\"#c8ff00\\\";\\n      ctx.fillText(`STABILITY: ONLINE")
# Wait, let's just do a direct replacement for the HUD block
hud_old = """      ctx.fillStyle = "#c8ff00";
      ctx.fillText(`STABILITY: STANDBY`, px + 15, py + 180);"""
hud_new = """      ctx.fillStyle = "#ff00ff";
      ctx.fillText(`FINGER COUNT: ${currentFingerCount}`, px + 15, py + 180);

      ctx.fillStyle = "#c8ff00";
      ctx.fillText(`STABILITY: ONLINE`, px + 15, py + 210);"""

# We'll use a safer replacement for the HUD
content = content.replace("STABILITY: STANDBY", "ONLINE")
content = content.replace("ctx.fillText(`STABILITY: ONLINE`, px + 15, py + 180);", 
                         "ctx.fillStyle = \"#ff00ff\";\\n      ctx.fillText(`FINGER COUNT: ${currentFingerCount}`, px + 15, py + 180);\\n\\n      ctx.fillStyle = \"#c8ff00\";\\n      ctx.fillText(`STABILITY: ONLINE`, px + 15, py + 210);")

# 3. Update hand results logic
content = content.replace("canvasCtx.save();\\n      if (results.multiHandLandmarks", 
                         "canvasCtx.save();\\n      currentFingerCount = 0;\\n      if (results.multiHandLandmarks")

content = content.replace("const upCount = fingersUp.filter(u => u).length;",
                         "const upCount = fingersUp.filter(u => u).length;\\n          currentFingerCount += upCount;")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully!")
