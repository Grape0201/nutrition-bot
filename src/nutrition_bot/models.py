from pydantic import BaseModel, Field

class Meal(BaseModel):
    eaten_at: str = Field(description="ISO8601形式の時刻")
    menu: str = Field(description="料理名")
    calories: int = Field(description="カロリー (kcal)")
    protein: float = Field(description="タンパク質 (g)")
    fat: float = Field(description="脂質 (g)")
    carb: float = Field(description="炭水化物 (g)")
    source_url: str | None = Field(description="参照したURL(任意)")

class MealAnalysisResult(BaseModel):
    meals: list[Meal] = Field(description="解析された食事のリスト")
