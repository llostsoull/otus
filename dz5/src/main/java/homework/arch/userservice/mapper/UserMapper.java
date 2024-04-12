package homework.arch.userservice.mapper;

import homework.arch.userservice.entity.UserEntity;
import homework.arch.userservice.dto.User;
import org.mapstruct.Mapper;

import java.util.List;

@Mapper
public interface UserMapper {
    User toDTO(UserEntity userEntity);
    UserEntity toEntity(User user);

    List<User> toDTO(List<UserEntity> userEntity);
    List<UserEntity> toEntity(List<User> user);    
}
