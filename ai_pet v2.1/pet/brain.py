import time
import random
import shutil
from pathlib import Path
from datetime import datetime
from config import (
    INITIAL_HUNGER, INITIAL_ENERGY, INITIAL_MOOD, INITIAL_HEALTH,
    HUNGER_DECAY, ENERGY_DECAY, MOOD_DECAY, HEALTH_DECAY,
    PET_FEED_HUNGER, PET_PET_MOOD, PET_PLAY_ENERGY, PET_PLAY_MOOD,
    PET_HEAL_HEALTH, PET_PET_AFFECTION, PET_PET_CLINGY,
    PET_PLAY_ACTIVE, PET_PLAY_CURIOUS, PET_SCOLD_MOOD,
    PET_SCOLD_AFFECTION, PET_SCOLD_STUBBORN,
    PET_BATHE_MOOD, PET_BATHE_HEALTH,
    PET_GIFT_MOOD, PET_GIFT_AFFECTION,
    PET_PRAISE_MOOD, PET_PRAISE_AFFECTION,
    PET_STORY_MOOD, PET_STORY_ENERGY,
    PET_TEACH_MOOD, PET_TEACH_ENERGY, PET_TEACH_CURIOUS,
    PET_DANCE_ENERGY, PET_DANCE_MOOD,
    DATA_DIR, ACTIONS, PET_NAME, FPS, bundled_path,
    ANIMAL_CONFIGS, COIN_REWARDS, GIFT_COST,
)
from pet.personality import Personality
from pet.memory import Memory
from pet.behavior import BehaviorEngine
from pet.dialogue import DialogueEngine
from brain_models.char_rnn import CharRNN


class Brain:
    def __init__(self):
        self.hunger = float(INITIAL_HUNGER)
        self.energy = float(INITIAL_ENERGY)
        self.mood = float(INITIAL_MOOD)
        self.health = float(INITIAL_HEALTH)
        self.last_tick = time.time()
        self.last_action_time = 0
        self.current_emotion = "happy"
        self.current_action = "idle"
        self.name = PET_NAME

        self.animal_type = "cat"
        self.animal_name = "橘猫"
        self.coins = 50
        self.shop_owned = ["cat"]
        self._load_shop()

        self.personality = Personality.load(self._animal_path())
        self.memory = Memory.load(self._animal_path())

        self.rnn = None
        weights_path = bundled_path("weights.npz")
        if weights_path.exists():
            try:
                self.rnn = CharRNN()
                self.rnn.load_weights(str(weights_path))
            except Exception:
                self.rnn = None

        self.behavior = BehaviorEngine.load(personality=self.personality)
        self.dialogue = DialogueEngine(personality=self.personality, memory=self.memory, rnn=self.rnn)

        self.last_dialogue = "你好呀~"
        self.emotion_timer = 0
        self.visual_overlay = None
        self.overlay_duration = 0
        self.overlay_max_duration = 0

    def tick(self):
        now = time.time()
        dt = now - self.last_tick
        self.last_tick = now

        self.hunger = min(100, self.hunger + HUNGER_DECAY * dt * 60)
        self.energy = max(0, self.energy - ENERGY_DECAY * dt * 60)
        self.mood = max(0, self.mood - MOOD_DECAY * dt * 60)
        if self.hunger > 80 or self.energy < 20:
            self.health = max(0, self.health - HEALTH_DECAY * dt * 60 * 2)
        else:
            self.health = max(0, self.health - HEALTH_DECAY * dt * 60)

        if self.emotion_timer > 0:
            self.emotion_timer -= 1
        else:
            self.current_emotion = self._determine_emotion()

        if self.overlay_duration > 0:
            self.overlay_duration -= 1
            if self.overlay_duration == 0:
                self.visual_overlay = None

        if now - self.last_action_time > 15:
            self._autonomous_action()
            self.last_action_time = now

    def _determine_emotion(self) -> str:
        if self.health < 30:
            return "sick"
        if self.hunger > 70:
            return "hungry"
        if self.energy < 30:
            return "sleepy"
        if self.mood < 30:
            return "sad"
        if self.mood > 85 and self.energy > 75:
            return "excited"
        if self.mood > 70 and self.energy > 60:
            return "playful"
        if self.energy > 50:
            return "curious"
        if self.mood > 60:
            return "happy"
        if self.mood > 40 and self.energy < 40:
            return "cuddly"
        return "idle"

    def _autonomous_action(self):
        hour = datetime.now().hour
        action = self.behavior.choose_action(self.hunger, self.energy, self.mood, self.health, hour)

        old_hunger, old_energy, old_mood, old_health = (
            self.hunger, self.energy, self.mood, self.health
        )

        if action == "sleep":
            self.energy = min(100, self.energy + 10)
            self.current_action = "sleepy"
        elif action == "eat":
            self.hunger = max(0, self.hunger - 15)
            self.current_action = "hungry"
        elif action == "explore":
            self.mood = min(100, self.mood + 5)
            self.current_action = "curious"
        elif action == "play":
            self.energy = max(0, self.energy - 10)
            self.mood = min(100, self.mood + 8)
            self.current_action = "playful"
        elif action == "cuddle":
            self.mood = min(100, self.mood + 5)
            self.current_action = "happy"
        elif action == "wander":
            self.mood = min(100, self.mood + 3)
            self.current_action = "curious"
        elif action == "groom":
            self.health = min(100, self.health + 3)
            self.current_action = "idle"

        reward = self.behavior.get_reward(action, old_hunger, old_energy, old_mood, old_health)
        self.behavior.update(
            old_hunger, old_energy, old_mood, old_health, hour,
            action, reward,
            self.hunger, self.energy, self.mood, self.health, hour,
        )

    def _pick_emotion(self, choices: list[tuple[str, str, int]]) -> tuple[str, str]:
        total = sum(w for _, _, w in choices)
        r = random.uniform(0, total)
        cum = 0
        for emo, act, w in choices:
            cum += w
            if r <= cum:
                return emo, act
        return choices[-1][0], choices[-1][1]

    def _set_overlay(self, overlay_type: str, duration: int = None):
        self.visual_overlay = overlay_type
        dur = duration or FPS * 2
        self.overlay_duration = dur
        self.overlay_max_duration = dur

    def interact(self, action_type: str) -> str:
        self.memory.remember(f"last_{action_type}")
        self.emotion_timer = FPS * 3
        self.coins += COIN_REWARDS.get(action_type, 0)

        if action_type == "gift":
            if self.coins < GIFT_COST:
                return f"金币不够了……需要 {GIFT_COST} 金币才能买礼物(′･_･`)"
            self.coins -= GIFT_COST

        if action_type == "pet":
            self.mood = min(100, self.mood + PET_PET_MOOD)
            self.personality.modify({"affectionate": PET_PET_AFFECTION, "clingy": PET_PET_CLINGY})
            self.memory.remember("last_petted", "被抚摸")
            self._set_overlay("heart")
            self.current_emotion, self.current_action = self._pick_emotion([
                ("happy", "happy", 5),
                ("curious", "curious", 2),
                ("sleepy", "sleepy", 1),
            ])
            return self.dialogue.generate("loving")
        elif action_type == "feed":
            self.hunger = max(0, self.hunger + PET_FEED_HUNGER)
            self.personality.modify({"affectionate": 0.02})
            foods = ["小鱼干", "猫粮", "零食", "鸡肉", "布丁"]
            food = random.choice(foods)
            self.memory.remember("last_food", food)
            self._set_overlay("food")
            self.current_emotion, self.current_action = self._pick_emotion([
                ("happy", "happy", 5),
                ("curious", "curious", 3),
                ("playful", "playful", 1),
            ])
            return self.dialogue.generate("grateful")
        elif action_type == "play":
            self.energy = max(0, self.energy + PET_PLAY_ENERGY)
            self.mood = min(100, self.mood + PET_PLAY_MOOD)
            self.personality.modify({"energetic": PET_PLAY_ACTIVE, "curious": PET_PLAY_CURIOUS})
            self.memory.remember("last_play", "玩耍")
            self._set_overlay("toy")
            self.current_emotion, self.current_action = self._pick_emotion([
                ("playful", "playful", 5),
                ("happy", "happy", 3),
                ("curious", "curious", 2),
            ])
            return self.dialogue.generate("playful")
        elif action_type == "heal":
            self.health = min(100, self.health + PET_HEAL_HEALTH)
            self.memory.remember("last_heal", "治疗")
            self._set_overlay("sparkle")
            self.current_emotion, self.current_action = self._pick_emotion([
                ("happy", "happy", 5),
                ("idle", "idle", 2),
                ("sleepy", "sleepy", 1),
            ])
            return self.dialogue.generate("grateful")
        elif action_type == "scold":
            self.mood = max(0, self.mood + PET_SCOLD_MOOD)
            self.personality.modify({
                "affectionate": PET_SCOLD_AFFECTION,
                "stubborn": PET_SCOLD_STUBBORN,
            })
            self._set_overlay("anger")
            self.current_emotion, self.current_action = self._pick_emotion([
                ("sad", "sad", 5),
                ("sleepy", "sleepy", 2),
                ("idle", "idle", 1),
            ])
            return self.dialogue.generate("sad")
        elif action_type == "greet":
            self.current_emotion, self.current_action = self._pick_emotion([
                ("happy", "happy", 5),
                ("curious", "curious", 3),
                ("playful", "playful", 2),
            ])
            return self.dialogue.generate_greeting()
        elif action_type == "bathe":
            self.mood = min(100, self.mood + PET_BATHE_MOOD)
            self.health = min(100, self.health + PET_BATHE_HEALTH)
            self._set_overlay("bubble", FPS * 3)
            self.current_emotion, self.current_action = self._pick_emotion([
                ("happy", "happy", 5),
                ("playful", "playful", 3),
                ("curious", "curious", 1),
            ])
            self.memory.remember("last_bathe", "洗澡")
            return self.dialogue.generate("grateful")
        elif action_type == "gift":
            self.mood = min(100, self.mood + PET_GIFT_MOOD)
            self.personality.modify({"affectionate": PET_GIFT_AFFECTION})
            gifts = ["蝴蝶结", "小铃铛",  "毛线球", "逗猫棒", "小毯子"]
            gift = random.choice(gifts)
            self.memory.remember("last_gift_item", gift)
            self._set_overlay("gift", FPS * 3)
            self.current_emotion, self.current_action = self._pick_emotion([
                ("excited", "excited", 5),
                ("happy", "happy", 3),
                ("playful", "playful", 1),
            ])
            return self.dialogue.generate("loving")
        elif action_type == "praise":
            self.mood = min(100, self.mood + PET_PRAISE_MOOD)
            self.personality.modify({"affectionate": PET_PRAISE_AFFECTION})
            self._set_overlay("star")
            self.current_emotion, self.current_action = self._pick_emotion([
                ("excited", "excited", 5),
                ("happy", "happy", 3),
                ("cuddly", "cuddly", 1),
            ])
            self.memory.remember("last_praise", "被称赞")
            return self.dialogue.generate("loving")
        elif action_type == "story":
            self.mood = min(100, self.mood + PET_STORY_MOOD)
            self.energy = max(0, self.energy + PET_STORY_ENERGY)
            self._set_overlay("book", FPS * 3)
            self.current_emotion, self.current_action = self._pick_emotion([
                ("curious", "curious", 5),
                ("happy", "happy", 2),
                ("sleepy", "sleepy", 2),
            ])
            stories = ["小猫钓鱼", "三只小猫", "猫和星星", "森林冒险"]
            self.memory.remember("last_story", random.choice(stories))
            return self.dialogue.generate("curious")
        elif action_type == "teach":
            self.mood = min(100, self.mood + PET_TEACH_MOOD)
            self.energy = max(0, self.energy + PET_TEACH_ENERGY)
            self.personality.modify({"curious": PET_TEACH_CURIOUS})
            self._set_overlay("sparkle")
            self.current_emotion, self.current_action = self._pick_emotion([
                ("curious", "curious", 4),
                ("playful", "playful", 3),
                ("happy", "happy", 2),
            ])
            tricks = ["握手", "打滚", "装死", "转圈"]
            self.memory.remember("last_trick", random.choice(tricks))
            return self.dialogue.generate("curious")
        elif action_type == "dance":
            self.energy = max(0, self.energy + PET_DANCE_ENERGY)
            self.mood = min(100, self.mood + PET_DANCE_MOOD)
            self._set_overlay("star")
            self.current_emotion, self.current_action = self._pick_emotion([
                ("dance", "dance", 5),
                ("excited", "excited", 3),
                ("happy", "happy", 1),
            ])
            self.memory.remember("last_dance", "跳舞")
            return self.dialogue.generate("playful")
        elif action_type == "status":
            return self.dialogue.generate_status(self.hunger, self.energy, self.mood, self.health)
        self.current_emotion, self.current_action = self._pick_emotion([
            ("curious", "curious", 4),
            ("happy", "happy", 2),
            ("idle", "idle", 1),
        ])
        return self.dialogue.generate("curious")

    def random_interact(self) -> str:
        actions = ["pet", "play", "greet"]
        return self.interact(random.choice(actions))

    def set_name(self, new_name: str):
        self.name = new_name
        self.memory.remember("name_changed", new_name)

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "hunger": round(self.hunger, 1),
            "energy": round(self.energy, 1),
            "mood": round(self.mood, 1),
            "health": round(self.health, 1),
            "emotion": self.current_emotion,
            "action": self.current_action,
        }

    def _animal_path(self) -> Path:
        p = DATA_DIR / self.animal_type
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _load_shop(self):
        path = DATA_DIR / "shop.json"
        if path.exists():
            import json
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
            self.coins = d.get("coins", 50)
            self.shop_owned = d.get("owned", ["cat"])
            self.animal_type = d.get("current", "cat")
            ac = ANIMAL_CONFIGS.get(self.animal_type, ANIMAL_CONFIGS["cat"])
            self.animal_name = ac["name"]

    def _save_shop(self):
        import json
        path = DATA_DIR / "shop.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "coins": self.coins,
                "owned": self.shop_owned,
                "current": self.animal_type,
            }, f, ensure_ascii=False, indent=2)

    def shop_get_coins(self):
        return self.coins

    def shop_buy(self, key: str, price: int):
        if self.coins < price or key in self.shop_owned:
            return
        self.coins -= price
        self.shop_owned.append(key)
        self.shop_switch(key)
        self._save_shop()

    def shop_switch(self, key: str):
        if key not in self.shop_owned:
            return
        self.save_all()
        old_type = self.animal_type
        self.animal_type = key
        ac = ANIMAL_CONFIGS.get(key, ANIMAL_CONFIGS["cat"])
        self.animal_name = ac["name"]
        self.personality = Personality.load(self._animal_path())
        self.memory = Memory.load(self._animal_path())
        self.behavior = BehaviorEngine.load(personality=self.personality)
        self.dialogue = DialogueEngine(personality=self.personality, memory=self.memory, rnn=self.rnn)
        self.load_state()
        self._save_shop()

    def save_all(self):
        self.personality.save(self._animal_path())
        self.memory.save(self._animal_path())
        self.behavior.save(self._animal_path())
        data = {
            "hunger": self.hunger,
            "energy": self.energy,
            "mood": self.mood,
            "health": self.health,
            "name": self.name,
        }
        path = self._animal_path() / "brain_state.json"
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self._save_shop()

    def load_state(self):
        path = self._animal_path() / "brain_state.json"
        if path.exists():
            import json
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.hunger = data.get("hunger", INITIAL_HUNGER)
            self.energy = data.get("energy", INITIAL_ENERGY)
            self.mood = data.get("mood", INITIAL_MOOD)
            self.health = data.get("health", INITIAL_HEALTH)
            self.name = data.get("name", PET_NAME)
