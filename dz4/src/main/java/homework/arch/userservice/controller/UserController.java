package homework.arch.userservice.controller;

import lombok.RequiredArgsConstructor;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import homework.arch.userservice.api.UserApi;
import homework.arch.userservice.dto.*;
import homework.arch.userservice.entity.UserEntity;
import homework.arch.userservice.mapper.UserMapper;
import homework.arch.userservice.service.UserService;


@RestController
@RequiredArgsConstructor
public class UserController implements UserApi {
    private final UserService userService;
    private final UserMapper userMapper;

    @Override
    public ResponseEntity<List<User>> getAllUsers(){
        return new ResponseEntity<>(userMapper.toDTO(userService.getAllUsers()), HttpStatus.OK);
    }

    @Override
    public ResponseEntity<User> createUser(User userDto){
        UserEntity savedUser = userService.createUser(userMapper.toEntity(userDto));
        return new ResponseEntity<>(userMapper.toDTO(savedUser), HttpStatus.CREATED);
    }

    @Override
    public ResponseEntity<User> findUserById(Long userId){
        System.out.println("userId" + userId);
        UserEntity user = userService.getUserById(userId);
        return new ResponseEntity<>(userMapper.toDTO(user), HttpStatus.OK);
    }

    @Override
    public ResponseEntity<User> updateUser(Long userId, User user){
        user.setId(userId);
        UserEntity updatedUser = userService.updateUser(userMapper.toEntity(user));
        return new ResponseEntity<>(userMapper.toDTO(updatedUser), HttpStatus.OK);
    }

    @Override
    public ResponseEntity<Void> deleteUser(Long userId){
        userService.deleteUser(userId);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }

}
