"""数据模型回归测试"""


def test_enum_columns_use_lowercase_values():
    """枚举列必须存储小写值，与 sql/init.sql 的 ENUM 定义保持一致"""
    from app.models.recipe import Meal, MealType, Recipe, RecipeStatus
    from app.models.user import Gender, User

    meal_enum = Meal.__table__.c.meal_type.type
    status_enum = Recipe.__table__.c.status.type
    gender_enum = User.__table__.c.gender.type

    assert set(meal_enum.enums) == {m.value for m in MealType}
    assert set(status_enum.enums) == {s.value for s in RecipeStatus}
    assert set(gender_enum.enums) == {g.value for g in Gender}
