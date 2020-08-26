from typing import List, Tuple

from tortoise import QuerySet
from tortoise.query_utils import Q

from jauth.model.user import User, UserType, UserStatus
from jauth.structure.datetime_range import DatetimeRange


def user_model_to_dict(row: User):
    user_dict = {
        'id': row.id,
        'email': row.email,
        'type': row.type,
        'status': row.status,
        'extra': row.extra,
        'is_email_verified': row.is_email_verified,
        'created_at': row.created_at,
        'modified_at': row.modified_at,
    }

    if row.type == UserType.EMAIL:
        user_dict['account'] = row.account

    if row.type != UserType.EMAIL:
        user_dict['third_party_user_id'] = row.third_party_user_id

    return user_dict


def _user_relational_query_set(query_set: QuerySet[User]) -> QuerySet[User]:
    return query_set


async def find_user_by_id(_id: str) -> User:
    return await _user_relational_query_set(
        User.filter(
            id=_id
        ).order_by(
            'modified_at', 'created_at'
        )
    ).first()


async def find_user_by_account(account: str) -> User:
    return await _user_relational_query_set(
        User.filter(
            account=account
        )
    ).first()


async def find_user_by_third_party_user_id(user_type: UserType, third_party_user_id: str) -> User:
    return await _user_relational_query_set(
        User.filter(
            third_party_user_id=third_party_user_id,
            type=user_type,
            status=UserStatus.NORMAL,
        )
    ).first()


async def search_users(
    emails: List[str] = (),
    created_at_range: DatetimeRange = None,
    modified_at_range: DatetimeRange = None,
    extra_text: List[str] = (),
    start: int = 0,
    size: int = 10,
    order_bys: List[str] = (),
    status: List[int] = (),
    types: List[int] = ()
) -> Tuple[int, List[User]]:
    if not status:
        status = [UserStatus.NORMAL]
    else:
        status = [UserStatus(e) for e in status]

    filters = []
    if extra_text:
        filters.append(Q(
            *[Q(extra__contains=word) for word in extra_text],
            join_type='OR'
        ))

    if emails:
        filters.append(Q(
            *[Q(email=email) for email in emails],
            join_type='OR'
        ))

    if created_at_range:
        filters.append(Q(
            created_at__gte=created_at_range.start,
            created_at__lte=created_at_range.end
        ))

    if modified_at_range:
        filters.append(Q(
            modified_at__gte=modified_at_range.start,
            modified_at__lte=modified_at_range.end
        ))

    if types:
        filters.append(Q(
            *[Q(type=type_) for type_ in types],
            join_type='OR'
        ))

    query_set = _user_relational_query_set(
        User.filter(
            Q(*filters)
        ).filter(status__in=status)
    ).all()

    for order_by in order_bys:
        if order_by.isascii():
            query_set = query_set.order_by(order_by)
    return (
        await query_set.count(),
        await query_set.offset(start).limit(size).all()
    )


async def create_user(
    user_type: UserType,
    email: str,
    account: str = None,
    hashed_password: str = None,
    third_party_user_id: str = None,
    extra: dict = None
) -> User:
    if extra is None:
        extra = {}

    return await User.create(
        type=user_type,
        account=account,
        email=email,
        hashed_password=hashed_password,
        third_party_user_id=third_party_user_id,
        extra=extra,
    )


async def update_user(
    user_id: str,
    **kwargs
) -> int:
    return await User.filter(
        id=user_id
    ).update(
        **kwargs
    )
