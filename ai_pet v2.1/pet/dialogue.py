import random
from config import PET_NAME, EMOTIONS, TEMPLATE_PROB
from brain_models.char_rnn import CharRNN


TEMPLATES = {
    "happy": [
        "我好开心！{name}你真好~",
        "今天真是美好的一天！",
        "嘿嘿，我好快乐！",
        "最喜欢和你在一起了~",
        "心情超棒的！",
        "我好幸福呀！{name}",
        "开心到转圈圈！",
        "和你在一起最开心了~",
    ],
    "sad": [
        "呜呜……心情不太好……",
        "有点难过……{name}陪陪我……",
        "感觉好孤单……",
        "心情低落的我……",
        "能抱抱我吗？",
        "今天不太开心……",
        "心里空空的……",
        "{name}……我好难过……",
    ],
    "hungry": [
        "我好饿呀……{name}有吃的吗？",
        "肚子咕咕叫了……",
        "想吃好吃的！",
        "饿饿……要吃饭！",
        "有什么可以吃的吗？",
        "好想吃东西呀~",
        "饿得没力气了……",
        "{name}，我饿了！",
    ],
    "sleepy": [
        "好困呀……想睡觉……",
        "眼睛睁不开了……",
        "想窝在被子里……",
        "困困的……好舒服……",
        "晚安啦……呼……",
        "好想打个盹~",
        "眼皮好重呀……",
        "困死了……要睡了……",
    ],
    "playful": [
        "来玩来玩！陪我玩~",
        "好有精神！一起玩吧！",
        "蹦蹦跳跳！好开心！",
        "我想玩游戏！",
        "追我呀追我呀~",
        "现在就出去玩！",
        "精力旺盛中！",
        "{name}，一起来玩吧！",
    ],
    "curious": [
        "那是什么呀？好在意！",
        "咦？你在干什么？",
        "好好奇呀~",
        "让我看看让我看看！",
        "这个是什么东西？",
        "咦咦？好有趣！",
        "我想知道！告诉我嘛~",
        "哇，发现了有趣的东西！",
    ],
    "grateful": [
        "谢谢你一直陪着我！",
        "有{name}在真好~",
        "谢谢你的照顾！",
        "我最喜欢{name}了！",
        "你对我真好，我好感动~",
        "感恩有你的每一天~",
        "谢谢谢谢！你最好啦！",
        "你真是世界上最好的人！",
    ],
    "loving": [
        "我爱你！{name}！",
        "最喜欢你了~",
        "嘿嘿，你是我的宝贝~",
        "好喜欢你呀！",
        "你是我最重要的人！",
        "我的心里都是你~",
        "你好好哦！超级喜欢！",
        "你就是我的全世界！",
    ],
    "excited": [
        "哇哇哇！好兴奋呀！",
        "太棒了！好开心好开心！",
        "{name}！我超级高兴！",
        "啊啊啊！激动到飞起！",
        "今天是最棒的一天！",
        "兴奋得停不下来！",
        "好激动好激动！",
        "太惊喜了！我爱这个！",
    ],
    "cuddly": [
        "抱抱我嘛~",
        "想被{name}抱在怀里~",
        "蹭蹭~好温暖~",
        "人家想要抱抱~",
        "好想缩在{name}怀里~",
        "让我靠靠嘛~",
        "抱一个嘛好不好~",
        "最温暖的怀抱~",
    ],
}


class DialogueEngine:
    def __init__(self, personality=None, memory=None, rnn: CharRNN = None):
        self.personality = personality
        self.memory = memory
        self.rnn = rnn

    def generate(self, emotion: str) -> str:
        if emotion not in TEMPLATES:
            emotion = "happy"

        use_rnn = self.rnn is not None and random.random() > TEMPLATE_PROB

        if use_rnn:
            try:
                seed = f"<{emotion}>"
                generated = self.rnn.sample(seed, length=25)
                generated = generated.replace(f"<{emotion}>", "").strip()
                if generated and len(generated) > 3:
                    return generated
            except Exception:
                pass

        templates = TEMPLATES.get(emotion, TEMPLATES["happy"])
        text = random.choice(templates)
        text = text.replace("{name}", PET_NAME)

        return text

    def generate_greeting(self) -> str:
        return random.choice([
            f"你好呀！{PET_NAME}在这里~",
            f"嗨！{PET_NAME}想你了！",
            "你回来啦！",
            "等你好久了~",
            "嘿！一起玩吧！",
            f"{PET_NAME}在此！有何指示？",
        ])

    def generate_status(self, hunger: float, energy: float, mood: float, health: float) -> str:
        status_parts = []
        if hunger > 70:
            status_parts.append("好饿")
        elif hunger < 30:
            status_parts.append("吃饱了")
        if energy > 70:
            status_parts.append("精神满满")
        elif energy < 30:
            status_parts.append("好累")
        if mood > 70:
            status_parts.append("心情很好")
        elif mood < 30:
            status_parts.append("不开心")
        if health > 70:
            status_parts.append("很健康")
        elif health < 30:
            status_parts.append("不舒服")

        if status_parts:
            return "我现在" + "，".join(status_parts) + "哦~"
        return "我感觉还不错~"
