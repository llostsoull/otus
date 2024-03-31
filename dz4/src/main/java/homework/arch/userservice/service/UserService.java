package homework.arch.userservice.service;

import homework.arch.userservice.repository.UserRepository;
import homework.arch.userservice.entity.UserEntity;
import org.springframework.stereotype.Service;
import lombok.RequiredArgsConstructor;
import java.util.Optional;

import java.util.List;

@Service("userServiceV1")
@RequiredArgsConstructor
public class UserService {
    private final UserRepository repository;

    public UserEntity createUser(UserEntity user){
        return repository.save(user);
    }

    public UserEntity getUserById(Long userId){
        Optional<UserEntity> optionalUser = repository.findById(userId);
        return optionalUser.get();
    }

    public List<UserEntity> getAllUsers(){
        return repository.findAll();
    }

    public UserEntity updateUser(UserEntity user){
        UserEntity existingUser = repository.findById(user.getId()).get();
        existingUser.setFirstName(user.getFirstName());
        existingUser.setLastName(user.getLastName());
        existingUser.setEmail(user.getEmail());
        UserEntity updatedUser = repository.save(existingUser);
        return updatedUser; 
    }

    public void deleteUser(Long userId){
        repository.deleteById(userId);
    }
}
