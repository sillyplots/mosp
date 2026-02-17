# Manual Download Instructions

YouTube's API is blocking our scripts, and the "official" YouTube download button saves encrypted files that Python cannot read.

**Please download these 9 songs manually.** 

You can use any "YouTube to MP3" converter website or tool you prefer.

### 1. The Pixies (Target)
Save these to: `posts/loud_quiet_loud/data/pixies/`

| Song | URL | Expected Filename |
|------|-----|-------------------|
| Debaser | [Link](https://www.youtube.com/watch?v=PVyS9JwtFoQ) | `Pixies_Debaser.mp3` |
| Tame | [Link](https://www.youtube.com/watch?v=2Yn3Ls5jZ4g) | `Pixies_Tame.mp3` |
| Gigantic | [Link](https://www.youtube.com/watch?v=xJncHEZ3URs) | `Pixies_Gigantic.mp3` |
| Where Is My Mind | [Link](https://www.youtube.com/watch?v=OJ62RzJkYUo) | `Pixies_Where_Is_My_Mind.mp3` |

### 2. Control Group (The 80s Predecessors)
Save these to: `posts/loud_quiet_loud/data/control/`

These bands were active just *before* or during the Pixies' rise (1984-1987) and represent the "landscape" before the Loud-Quiet-Loud dynamic took over. They tend to be "Always Loud" (Hüsker Dü) or "Always Jangly" (R.E.M.).

| Band | Song | URL | Why? |
|------|------|-----|------|
| **Hüsker Dü** | *Don't Want to Know If You Are Lonely* | [Link](https://www.youtube.com/watch?v=Gto6v_e37kI) | Constant, driving intensity (Pre-Pixies Loud) |
| **The Replacements** | *Bastards of Young* | [Link](https://www.youtube.com/watch?v=fl9KQ1Mub6Q) | Straight-forward rock dynamic |
| **R.E.M.** | *Driver 8* | [Link](https://www.youtube.com/watch?v=wuFId1RuySE) | Consistent "jangly" texture (The "alternative" baseline) |
| **Sonic Youth** | *Schizophrenia* | [Link](https://www.youtube.com/watch?v=Nq3x6z_h3hA) | Noise rock, but often a "wall of sound" rather than strict switching |
| **The Jesus and Mary Chain** | *Just Like Honey* | [Link](https://www.youtube.com/watch?v=7EgB__YratE) | Constant fuzz/noise layer |
| **Meat Puppets** | *Plateau* | [Link](https://www.youtube.com/watch?v=64pX5I-6jEQ) | "Cow Punk" - distinct but steady lo-fi dynamic |
| **The Gun Club** | *Sex Beat* | [Link](https://www.youtube.com/watch?v=6L2KykG8DQU) | "Punk Blues" - driving, frantic energy without the "drop" |
| **Mission of Burma** | *That's When I Reach For My Revolver* | [Link](https://www.youtube.com/watch?v=4fcJO928yME) | Post-Punk anthem - loud and anthemic throughout |

### Next Step
Once you have downloaded **at least one** file for each group, run:
```bash
python posts/loud_quiet_loud/analyze_dynamics.py
```
