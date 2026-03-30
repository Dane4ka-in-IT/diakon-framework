package dev.diakon.nocodeplatform.service;

import dev.diakon.nocodeplatform.entity.User;
import dev.diakon.nocodeplatform.exeption.DuplicateEmailException;
import dev.diakon.nocodeplatform.exeption.InvalidPassword;
import dev.diakon.nocodeplatform.exeption.UserNotFound;
import dev.diakon.nocodeplatform.repositiry.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;


@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
    private final BCryptPasswordEncoder passwordEncoder;

    public void registerUser(User user){
        userRepository.findByUserEmail(user.getUserEmail())
                .ifPresentOrElse(
                        i -> {throw new DuplicateEmailException("Этот email уже используется");},
                        () -> {
                            String pass = passwordEncoder.encode(user.getUserPassword());
                            user.setUserPassword(pass);
                            userRepository.save(user);
                            System.out.println("Юзер успешно добавлен!");
                        });
    }

    public void loginUser(String email, String password){
        userRepository.findByUserEmail(email)
                .ifPresentOrElse(
                        i -> {
                            if (!passwordEncoder.matches(password, i.getUserPassword())){
                                throw new InvalidPassword("Невалидный логин или пароль");
                            };
                        },
                        () -> {
                            throw new UserNotFound("Юзер отсутствует в базе данных.");
                        }
                );
    }

    public void togglePremium(Long userId) {
        userRepository.findById(userId).
                ifPresentOrElse(user -> {
                        user.setIsPremium(!user.getIsPremium());
                        userRepository.save(user);
                        System.out.println("Статус премиума для " + user.getUserName() + " изменен на: " + user.getIsPremium());
                        },
                        () -> {
                            throw new UserNotFound("Юзера не существует!");
                        }
                );
    }
}
